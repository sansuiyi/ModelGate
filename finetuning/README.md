---
language:
  - en
license: apache-2.0
library_name: llama-cpp-python
base_model: katanemo/Arch-Router-1.5B
tags:
  - routing
  - grpo
  - reinforcement-learning
  - gguf
  - lora
  - unsloth
  - trl
  - qwen2
  - llama-cpp
  - contract-aware
  - cost-optimization
  - query-classification
model_type: qwen2
pipeline_tag: text-classification
datasets:
  - custom
metrics:
  - accuracy
model-index:
  - name: ModelGate-Router
    results:
      - task:
          type: text-classification
          name: Query Complexity Classification
        metrics:
          - type: accuracy
            value: 83.3
            name: Overall Accuracy (held-out, GGUF Q8_0)
          - type: accuracy
            value: 85.7
            name: Medium Tier Accuracy
          - type: latency
            value: 62
            name: Avg Latency (ms, CUDA)
---

# ModelGate-Router

GRPO (Group Relative Policy Optimization) fine-tuned routing model for ModelGate's contract-aware query routing. Based on Arch-Router-1.5B. Classifies incoming queries as **simple**, **medium**, or **complex** to route them to the right model tier.

## Results

### Accuracy — Held-Out Eval (54 unseen prompts, zero training overlap)

| Tier | Stock Arch-Router | ModelGate-Router | Improvement |
|------|-------------------|---------------|-------------|
| Simple (33) | 87.9% | 81.8% | -6.1% |
| **Medium (14)** | **14.3%** | **85.7%** | **+71.4%** |
| Complex (7) | 100.0% | 85.7% | -14.3% |
| **Overall (54)** | **70.4%** | **83.3%** | **+13.0%** |

The stock model misclassifies **86% of medium queries** as complex — routing them to expensive premium models when a mid-tier model would suffice. ModelGate-Router fixes this.

### Latency — GGUF Q8_0 + CUDA (RTX 3080 Laptop)

| Metric | Stock | ModelGate-Router | Delta |
|--------|-------|---------------|-------|
| Avg | 62.6ms | 61.7ms | -0.9ms |
| P50 | 61.3ms | 60.5ms | -0.8ms |
| P95 | 67.8ms | 67.3ms | -0.5ms |

**Zero latency overhead.** ModelGate-Router is actually marginally faster.

### Latency by Inference Backend

| Backend | Model Size | Avg Latency | vs Transformers FP16 |
|---------|-----------|-------------|---------------------|
| Transformers FP16 | ~3.0 GB | 196ms | baseline |
| GGUF Q8_0 (CPU) | 1.6 GB | 768ms | 3.9x slower |
| **GGUF Q8_0 (CUDA)** | **1.6 GB** | **62ms** | **3.2x faster** |

### Quantization Impact on Accuracy

| Backend | Stock Accuracy | ModelGate-Router Accuracy |
|---------|---------------|-------------------|
| Transformers FP16 | 72.2% | 81.5% |
| GGUF Q8_0 | 70.4% | 83.3% |

Q8_0 quantization causes **no meaningful accuracy degradation**.

### Chain-of-Thought vs Direct Output

We trained two variants — one with chain-of-thought reasoning (`<reasoning>` tags before the answer) and one with direct JSON output. Results on held-out data:

| Variant | Accuracy | Avg Latency | Verdict |
|---------|----------|-------------|---------|
| Stock | 72.2% | 196ms | Baseline |
| **ModelGate-Router (No-CoT)** | **81.5%** | **198ms** | **Best tradeoff** |
| ModelGate-Router (CoT) | 61.1% | 1,787ms | Overfit, 9x slower |

The CoT variant actually hurt accuracy on unseen data (overfit to training format) and added ~1.6s of latency per classification. The No-CoT variant is the clear winner.

## Why Fine-Tune?

The stock `katanemo/Arch-Router-1.5B` was trained for general-purpose intent routing. Our use case is specific: classify queries across customer support, insurance claims, and device protection into three complexity tiers. The stock model has a critical blind spot — it routes nearly all medium-complexity queries to the complex tier, wasting money on premium models.

## Architecture

```
Qwen/Qwen2.5-1.5B-Instruct           (base LLM, 1.5B params)
     |
     v  Katanemo fine-tune
katanemo/Arch-Router-1.5B             (general intent routing)
     |
     v  GRPO fine-tune (2.3% of params, LoRA rank 32)
ModelGate-Router                       (domain-specific complexity routing)
     |
     v  GGUF Q8_0 quantization
ModelGate-Router.Q8_0.gguf            (1.6 GB, production-ready)
```

## Files

### Model Weights

| File | Size | Description |
|------|------|-------------|
| `ModelGate-Router.Q8_0.gguf` | 1.6 GB | ModelGate-Router — GGUF Q8_0, deploy with llama.cpp |
| `stock_arch_router.Q8_0.gguf` | 1.6 GB | Stock Arch-Router in GGUF Q8_0, for comparison |
| `ModelGate-Router-LoRA/` | 157 MB | ModelGate-Router LoRA adapter (best model) |
| `modelgate_arch_router_lora/` | 157 MB | CoT LoRA adapter (for reference only) |

### Data

| File | Description |
|------|-------------|
| `grpo_training_data.json` | 172 labeled training prompts across 4 domains |
| `grpo_eval_data.json` | 54 held-out eval prompts (zero overlap with training) |

### Scripts

| File | Description |
|------|-------------|
| `grpo_finetune_arch_router.ipynb` | CoT training notebook (Colab/local) |
| `grpo_run_nocot.py` | No-CoT training script (the one that produced the best model) |
| `export_gguf.py` | Merges LoRA + converts to GGUF Q8_0 |
| `bench_gguf.py` | Benchmarks GGUF models via llama.cpp (accuracy + latency) |
| `bench_stock_vs_finetune.py` | Benchmarks via Transformers (FP16, 3-way comparison) |

## Training Data

**172 training examples** across 4 domains and 3 tiers:

| Domain | Count |
|--------|-------|
| customer_support | 51 |
| insurance_claims | 46 |
| device_protection | 37 |
| general | 38 |

| Tier | Count | Examples |
|------|-------|----------|
| simple | 95 | "What is your return policy?", "Is my claim approved?" |
| medium | 51 | "Compare the protection plans available for my new laptop..." |
| complex | 26 | "Analyze the multi-party liability exposure across claims..." |

**54 eval examples** — completely separate prompts, same domain/tier distribution, zero overlap with training data.

## How GRPO Training Works

Unlike supervised fine-tuning where you provide input-output pairs, GRPO:

1. **Generates** multiple candidate completions per prompt
2. **Scores** each with reward functions
3. **Reinforces** the best completions relative to the group

### No-CoT Reward Functions

| Function | Max Score | Purpose |
|----------|-----------|---------|
| `correctness_reward_func` | 2.0 | Route matches ground truth |
| `valid_route_reward_func` | 0.5 | Output is a valid tier name |
| `json_format_reward_func` | 1.0 | Output is clean JSON with "route" key |
| `brevity_reward_func` | 0.5 | Rewards short outputs (just the JSON) |

## Training Details

| Parameter | Value |
|-----------|-------|
| Base model | `katanemo/Arch-Router-1.5B` |
| Method | GRPO via Unsloth + TRL |
| LoRA rank | 32 |
| Trainable params | 36.9M / 1.58B (2.3%) |
| Training steps | 150 |
| Training time | **2.5 minutes** |
| Hardware | RTX 3080 Laptop 8GB |
| VRAM usage | ~6 GB (4-bit quantized during training) |
| Generations per prompt | 4 |
| Learning rate | 5e-6 |
| Max completion length | 64 tokens |

## How to Reproduce

### Train the No-CoT Model

```bash
# Requires: pip install unsloth vllm trl
python finetuning/grpo_run_nocot.py
# Output: ModelGate-Router-LoRA/
```

### Export to GGUF

```bash
python finetuning/export_gguf.py nocot
# Output: finetuning/ModelGate-Router.Q8_0.gguf
```

### Benchmark

```bash
# GGUF benchmark (requires llama-cpp-python with CUDA)
python finetuning/bench_gguf.py

# Transformers FP16 benchmark (3-way: stock vs no-CoT vs CoT)
python finetuning/bench_stock_vs_finetune.py
```

## Production Deployment

The recommended deployment uses `ModelGate-Router.Q8_0.gguf` with llama.cpp:

```python
from llama_cpp import Llama

model = Llama(
    model_path="finetuning/ModelGate-Router.Q8_0.gguf",
    n_ctx=512,
    n_gpu_layers=-1,  # All layers on GPU
)

# Classify a query
response = model.create_chat_completion(
    messages=[{"role": "user", "content": routing_prompt}],
    max_tokens=30,
    temperature=0,
)
route = json.loads(response["choices"][0]["message"]["content"])["route"]
# route is "simple", "medium", or "complex"
```

**Expected performance**: ~62ms per classification, 83%+ accuracy, 1.6 GB VRAM.

## Route Policies

The three tiers the model classifies into (defined in `backend/services/classifier.py`):

| Tier | Description | Model Tier | Cost |
|------|-------------|-----------|------|
| simple | FAQs, status checks, basic lookups | gpt-4o-mini, gemini-flash | $0.10-0.60/M tokens |
| medium | Multi-step reasoning, comparisons, troubleshooting | gpt-4o, claude-sonnet | $2.50-15.00/M tokens |
| complex | Multi-document analysis, legal/financial reasoning | gemini-2.5-pro, claude-sonnet | $2.50-15.00/M tokens |

Correctly routing simple queries to cheap models instead of premium ones is the core value proposition. The stock model's 14% medium accuracy means it wastes money routing mid-tier queries to expensive models. ModelGate-Router's 86% medium accuracy captures those savings.

## References

- [Arch-Router-1.5B](https://huggingface.co/katanemo/Arch-Router-1.5B) — base model
- [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) — foundation model
- [Unsloth](https://github.com/unslothai/unsloth) — training framework
- [TRL GRPOTrainer](https://huggingface.co/docs/trl/main/en/grpo_trainer) — GRPO implementation
- [llama.cpp](https://github.com/ggerganov/llama.cpp) — GGUF inference engine
