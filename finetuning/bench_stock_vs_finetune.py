#!/usr/bin/env python3
"""
Benchmark: Stock Arch-Router-1.5B vs GRPO Fine-Tuned
=====================================================
Compares classification accuracy and latency between the stock model
and our GRPO fine-tune with chain-of-thought reasoning.
"""

import json
import time
import torch
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

DATA_PATH = Path(__file__).parent / "grpo_eval_data.json"
LORA_COT_PATH = Path(__file__).parent / "modelgate_arch_router_lora"
LORA_NOCOT_PATH = Path(__file__).parent / "modelgate_arch_router_nocot_lora"
BASE_MODEL = "katanemo/Arch-Router-1.5B"

ROUTE_POLICIES = [
    {"name": "simple", "description": "Simple factual questions, greetings, basic lookups, yes/no answers, FAQ-style queries, single-step tasks, status checks, straightforward requests"},
    {"name": "medium", "description": "Multi-step reasoning, summarization of moderate-length text, data extraction, moderate analysis, comparison tasks, troubleshooting, explanations requiring some depth"},
    {"name": "complex", "description": "Complex multi-document reasoning, deep analysis, legal or financial interpretation, creative writing, code generation, multi-constraint problem solving, liability assessment, comprehensive evaluation"},
]


def build_stock_prompt(prompt: str) -> str:
    """Prompt format used by stock Arch-Router (matches classifier.py)."""
    policies_json = json.dumps(ROUTE_POLICIES)
    conversation_json = json.dumps([{"role": "user", "content": prompt}])
    return f"""You are a routing assistant. Given the route policies and user message, select the best matching route.

<route_policies>
{policies_json}
</route_policies>

<conversation>
{conversation_json}
</conversation>

Select the best route for this user message. Respond with ONLY valid JSON: {{"route": "route_name"}}"""


def build_cot_prompt(prompt: str) -> str:
    """Prompt format for the GRPO fine-tune with chain-of-thought."""
    policies_json = json.dumps(ROUTE_POLICIES)
    conversation_json = json.dumps([{"role": "user", "content": prompt}])
    return f"""You are a routing assistant. Given the route policies and user message, select the best matching route.

<route_policies>
{policies_json}
</route_policies>

<conversation>
{conversation_json}
</conversation>

Respond in the following format:
<reasoning>
...analyze the query complexity, considering factors like: number of tasks requested, depth of analysis needed, domain specificity, and whether it requires multi-step reasoning...
</reasoning>
<answer>
{{"route": "route_name"}}
</answer>"""


def extract_route_stock(text: str) -> str | None:
    """Parse route from stock model output (raw JSON)."""
    try:
        parsed = json.loads(text.strip())
        route = parsed.get("route")
        if route in ("simple", "medium", "complex"):
            return route
    except json.JSONDecodeError:
        pass
    for tier in ("simple", "medium", "complex"):
        if tier in text.lower():
            return tier
    return None


def extract_route_cot(text: str) -> str | None:
    """Parse route from CoT model output (<answer> tags)."""
    if "<answer>" in text:
        answer_text = text.split("<answer>")[-1].split("</answer>")[0].strip()
        try:
            parsed = json.loads(answer_text)
            route = parsed.get("route")
            if route in ("simple", "medium", "complex"):
                return route
        except (json.JSONDecodeError, TypeError):
            pass
    # Fallback to stock parsing
    return extract_route_stock(text)


def run_benchmark(model, tokenizer, data, prompt_fn, extract_fn, max_new_tokens, label):
    results = {"correct": 0, "total": 0, "latencies_ms": [], "by_tier": {}, "misclassifications": []}

    for i, item in enumerate(data):
        prompt_text = prompt_fn(item["prompt"])
        inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)

        torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.0,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        torch.cuda.synchronize()
        elapsed_ms = (time.perf_counter() - start) * 1000

        new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        predicted = extract_fn(response)
        expected = item["expected_route"]
        correct = predicted == expected

        results["total"] += 1
        results["latencies_ms"].append(elapsed_ms)
        if correct:
            results["correct"] += 1

        if expected not in results["by_tier"]:
            results["by_tier"][expected] = {"correct": 0, "total": 0, "latencies": []}
        results["by_tier"][expected]["total"] += 1
        results["by_tier"][expected]["latencies"].append(elapsed_ms)
        if correct:
            results["by_tier"][expected]["correct"] += 1
        else:
            results["misclassifications"].append({
                "prompt": item["prompt"][:80],
                "expected": expected,
                "predicted": predicted,
                "response": response[:100],
            })

        status = "✓" if correct else "✗"
        print(f"  [{i+1:3d}/{len(data)}] {status} [{expected:>7s}→{str(predicted):<7s}] {elapsed_ms:6.1f}ms | {item['prompt'][:55]}")

    return results


def print_results(results, label):
    print(f"\n{'='*65}")
    print(f"  {label}")
    print(f"{'='*65}")

    for tier in ("simple", "medium", "complex"):
        if tier in results["by_tier"]:
            t = results["by_tier"][tier]
            pct = t["correct"] / t["total"] * 100 if t["total"] else 0
            avg_lat = sum(t["latencies"]) / len(t["latencies"])
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {tier:<10s} {t['correct']:>2d}/{t['total']:<2d} ({pct:5.1f}%) {bar}  avg {avg_lat:6.1f}ms")

    total_pct = results["correct"] / results["total"] * 100
    avg_latency = sum(results["latencies_ms"]) / len(results["latencies_ms"])
    p50 = sorted(results["latencies_ms"])[len(results["latencies_ms"]) // 2]
    p95 = sorted(results["latencies_ms"])[int(len(results["latencies_ms"]) * 0.95)]

    print(f"\n  OVERALL:  {results['correct']}/{results['total']} ({total_pct:.1f}%)")
    print(f"  Latency:  avg {avg_latency:.1f}ms | p50 {p50:.1f}ms | p95 {p95:.1f}ms")

    if results["misclassifications"]:
        print(f"\n  MISCLASSIFICATIONS ({len(results['misclassifications'])}):")
        for m in results["misclassifications"][:10]:
            print(f"    {m['expected']}→{m['predicted']}: {m['prompt']}")
    print(f"{'='*65}\n")

    return {"accuracy": total_pct, "avg_ms": avg_latency, "p50_ms": p50, "p95_ms": p95}


def main():
    with open(DATA_PATH) as f:
        data = json.load(f)

    print(f"Loaded {len(data)} eval prompts\n")

    # ── Load stock model ──
    print("Loading stock Arch-Router-1.5B...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    stock_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, torch_dtype=torch.float16, device_map="cuda"
    )
    stock_model.eval()

    # Warmup
    warmup_input = tokenizer(build_stock_prompt("Hello"), return_tensors="pt").to(stock_model.device)
    with torch.inference_mode():
        stock_model.generate(**warmup_input, max_new_tokens=10)
    print("Stock model ready\n")

    # ── Run stock benchmark ──
    print("Running stock model benchmark...")
    stock_results = run_benchmark(
        stock_model, tokenizer, data,
        prompt_fn=build_stock_prompt,
        extract_fn=extract_route_stock,
        max_new_tokens=30,
        label="Stock"
    )
    stock_stats = print_results(stock_results, "STOCK Arch-Router-1.5B (max_new_tokens=30)")

    # ── Load No-CoT fine-tuned model ──
    print("Loading GRPO No-CoT fine-tuned model (LoRA)...")
    nocot_model = PeftModel.from_pretrained(stock_model, str(LORA_NOCOT_PATH))
    nocot_model = nocot_model.merge_and_unload()
    nocot_model.eval()

    # Warmup
    warmup_input = tokenizer(build_stock_prompt("Hello"), return_tensors="pt").to(nocot_model.device)
    with torch.inference_mode():
        nocot_model.generate(**warmup_input, max_new_tokens=30)
    print("No-CoT fine-tuned model ready\n")

    # ── Run No-CoT benchmark ──
    print("Running No-CoT fine-tuned model benchmark...")
    nocot_results = run_benchmark(
        nocot_model, tokenizer, data,
        prompt_fn=build_stock_prompt,
        extract_fn=extract_route_stock,
        max_new_tokens=30,  # Same as stock — no reasoning tokens
        label="No-CoT Fine-tuned"
    )
    nocot_stats = print_results(nocot_results, "GRPO Fine-Tuned No-CoT (max_new_tokens=30)")

    del nocot_model
    torch.cuda.empty_cache()

    # ── Load CoT fine-tuned model ──
    print("Loading GRPO CoT fine-tuned model (LoRA)...")
    stock_model2 = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, torch_dtype=torch.float16, device_map="cuda"
    )
    cot_model = PeftModel.from_pretrained(stock_model2, str(LORA_COT_PATH))
    cot_model = cot_model.merge_and_unload()
    cot_model.eval()

    # Warmup
    warmup_input = tokenizer(build_cot_prompt("Hello"), return_tensors="pt").to(cot_model.device)
    with torch.inference_mode():
        cot_model.generate(**warmup_input, max_new_tokens=100)
    print("CoT fine-tuned model ready\n")

    # ── Run CoT benchmark ──
    print("Running CoT fine-tuned model benchmark...")
    cot_results = run_benchmark(
        cot_model, tokenizer, data,
        prompt_fn=build_cot_prompt,
        extract_fn=extract_route_cot,
        max_new_tokens=150,
        label="CoT Fine-tuned"
    )
    cot_stats = print_results(cot_results, "GRPO Fine-Tuned CoT (max_new_tokens=150)")

    # ── 3-Way Comparison ──
    print(f"{'='*75}")
    print(f"  COMPARISON: Stock vs No-CoT vs CoT")
    print(f"{'='*75}")
    print(f"  {'':20s} {'Stock':>12s} {'No-CoT FT':>12s} {'CoT FT':>12s}")
    print(f"  {'Accuracy':20s} {stock_stats['accuracy']:>11.1f}% {nocot_stats['accuracy']:>11.1f}% {cot_stats['accuracy']:>11.1f}%")
    print(f"  {'Avg latency':20s} {stock_stats['avg_ms']:>10.1f}ms {nocot_stats['avg_ms']:>10.1f}ms {cot_stats['avg_ms']:>10.1f}ms")
    print(f"  {'P50 latency':20s} {stock_stats['p50_ms']:>10.1f}ms {nocot_stats['p50_ms']:>10.1f}ms {cot_stats['p50_ms']:>10.1f}ms")
    print(f"  {'P95 latency':20s} {stock_stats['p95_ms']:>10.1f}ms {nocot_stats['p95_ms']:>10.1f}ms {cot_stats['p95_ms']:>10.1f}ms")
    print(f"{'='*75}")


if __name__ == "__main__":
    main()
