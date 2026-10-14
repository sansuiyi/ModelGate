#!/usr/bin/env python3
"""
GRPO Fine-Tune WITHOUT Chain-of-Thought
Trains Arch-Router-1.5B to output just {"route": "..."} with better accuracy,
no reasoning overhead.
"""

from unsloth import FastLanguageModel, is_bfloat16_supported
import torch
import re
import json
from datasets import Dataset
from collections import Counter

# ── Model loading ──
max_seq_length = 512
lora_rank = 32

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="katanemo/Arch-Router-1.5B",
    max_seq_length=max_seq_length,
    load_in_4bit=True,
    fast_inference=True,
    max_lora_rank=lora_rank,
    gpu_memory_utilization=0.6,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=lora_rank,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=lora_rank,
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)

# ── Route policies ──
ROUTE_POLICIES = [
    {"name": "simple", "description": "Simple factual questions, greetings, basic lookups, yes/no answers, FAQ-style queries, single-step tasks, status checks, straightforward requests"},
    {"name": "medium", "description": "Multi-step reasoning, summarization of moderate-length text, data extraction, moderate analysis, comparison tasks, troubleshooting, explanations requiring some depth"},
    {"name": "complex", "description": "Complex multi-document reasoning, deep analysis, legal or financial interpretation, creative writing, code generation, multi-constraint problem solving, liability assessment, comprehensive evaluation"},
]

# System prompt - NO chain of thought, just direct JSON output
SYSTEM_PROMPT = f"""You are a routing assistant. Given the route policies and user message, select the best matching route.

<route_policies>
{json.dumps(ROUTE_POLICIES)}
</route_policies>

Select the best route for this user message. Respond with ONLY valid JSON: {{"route": "route_name"}}"""


def extract_route(text: str) -> str | None:
    try:
        parsed = json.loads(text.strip())
        route = parsed.get("route")
        if route in ("simple", "medium", "complex"):
            return route
    except (json.JSONDecodeError, TypeError):
        pass
    for tier in ("simple", "medium", "complex"):
        if tier in text.lower():
            return tier
    return None


# ── Load training data ──
import os
DATA_PATHS = ["scripts/grpo_training_data.json", "grpo_training_data.json", "/content/grpo_training_data.json"]
data_path = next((p for p in DATA_PATHS if os.path.exists(p)), None)
if data_path is None:
    raise FileNotFoundError("Training data not found")

with open(data_path) as f:
    raw_data = json.load(f)

print(f"Loaded {len(raw_data)} training examples")

formatted = []
for item in raw_data:
    formatted.append({
        "prompt": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": item["prompt"]},
        ],
        "answer": item["expected_route"],
    })

dataset = Dataset.from_list(formatted)
print(f"Route distribution: {dict(Counter(item['expected_route'] for item in raw_data))}")


# ── Reward functions (no XML/format rewards - just correctness + valid JSON) ──
def correctness_reward_func(prompts, completions, answer, **kwargs) -> list[float]:
    responses = [completion[0]["content"] for completion in completions]
    extracted = [extract_route(r) for r in responses]
    q = prompts[0][-1]["content"]
    print(f"--- Q: {q[:60]} | Expected: {answer[0]} | Got: {extracted[0]} | Raw: {responses[0][:80]}")
    return [2.0 if r == a else 0.0 for r, a in zip(extracted, answer)]


def valid_route_reward_func(completions, **kwargs) -> list[float]:
    responses = [completion[0]["content"] for completion in completions]
    extracted = [extract_route(r) for r in responses]
    return [0.5 if r in ("simple", "medium", "complex") else 0.0 for r in extracted]


def json_format_reward_func(completions, **kwargs) -> list[float]:
    responses = [completion[0]["content"] for completion in completions]
    rewards = []
    for r in responses:
        try:
            parsed = json.loads(r.strip())
            if "route" in parsed:
                rewards.append(1.0)  # Higher reward for clean JSON
            else:
                rewards.append(0.2)
        except (json.JSONDecodeError, TypeError):
            rewards.append(0.0)
    return rewards


def brevity_reward_func(completions, **kwargs) -> list[float]:
    """Reward shorter outputs — we want just the JSON, nothing else."""
    responses = [completion[0]["content"] for completion in completions]
    rewards = []
    for r in responses:
        length = len(r.strip())
        if length <= 25:  # {"route": "complex"} is 21 chars
            rewards.append(0.5)
        elif length <= 50:
            rewards.append(0.2)
        else:
            rewards.append(0.0)
    return rewards


# ── Training ──
from trl import GRPOConfig, GRPOTrainer

training_args = GRPOConfig(
    use_vllm=True,
    learning_rate=5e-6,
    adam_beta1=0.9,
    adam_beta2=0.99,
    weight_decay=0.1,
    warmup_ratio=0.1,
    lr_scheduler_type="cosine",
    optim="adamw_8bit",
    logging_steps=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    num_generations=4,
    max_prompt_length=384,
    max_completion_length=64,   # Much shorter - just need JSON output
    max_steps=150,
    save_steps=150,
    max_grad_norm=0.1,
    report_to="none",
    output_dir="outputs_modelgate_nocot",
)

trainer = GRPOTrainer(
    model=model,
    processing_class=tokenizer,
    reward_funcs=[
        json_format_reward_func,
        valid_route_reward_func,
        brevity_reward_func,
        correctness_reward_func,
    ],
    args=training_args,
    train_dataset=dataset,
)
trainer.train()

# ── Save ──
model.save_pretrained("modelgate_arch_router_nocot_lora")
tokenizer.save_pretrained("modelgate_arch_router_nocot_lora")
print("\nLoRA adapter saved to modelgate_arch_router_nocot_lora/")

# ── Quick test ──
from vllm import SamplingParams

model.save_lora("modelgate_nocot_test_lora")
sampling_params = SamplingParams(temperature=0.8, top_p=0.95, max_tokens=30)

test_prompts = [
    ("What is your return policy?", "simple"),
    ("Compare the settlement amounts for similar property damage claims in the Southeast region this quarter.", "medium"),
    ("Analyze the multi-party liability exposure across claims #8901, #8902, and #8903 from the warehouse incident.", "complex"),
]

for prompt_text, expected in test_prompts:
    text = tokenizer.apply_chat_template([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt_text},
    ], tokenize=False, add_generation_prompt=True)
    output = model.fast_generate(
        [text], sampling_params=sampling_params,
        lora_request=model.load_lora("modelgate_nocot_test_lora"),
    )[0].outputs[0].text
    route = extract_route(output)
    status = "✓" if route == expected else "✗"
    print(f"{status} Expected: {expected:>7s} | Got: {str(route):>7s} | Raw: {output[:60]}")
