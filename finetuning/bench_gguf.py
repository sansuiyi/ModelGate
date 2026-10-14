#!/usr/bin/env python3
"""
Benchmark GGUF models via llama-cpp-python.
Compares stock vs no-CoT fine-tuned Arch-Router-1.5B in Q8_0 GGUF format.
"""

import json
import time
from pathlib import Path
from llama_cpp import Llama

EVAL_PATH = Path(__file__).parent / "grpo_eval_data.json"
STOCK_GGUF = Path(__file__).parent / "stock_arch_router.Q8_0.gguf"
NOCOT_GGUF = Path(__file__).parent / "nocot_arch_router.Q8_0.gguf"

ROUTE_POLICIES = [
    {"name": "simple", "description": "Simple factual questions, greetings, basic lookups, yes/no answers, FAQ-style queries, single-step tasks, status checks, straightforward requests"},
    {"name": "medium", "description": "Multi-step reasoning, summarization of moderate-length text, data extraction, moderate analysis, comparison tasks, troubleshooting, explanations requiring some depth"},
    {"name": "complex", "description": "Complex multi-document reasoning, deep analysis, legal or financial interpretation, creative writing, code generation, multi-constraint problem solving, liability assessment, comprehensive evaluation"},
]


def find_gguf(directory: Path) -> Path:
    """Find the .gguf file in a directory."""
    for f in directory.iterdir():
        if f.suffix == ".gguf":
            return f
    raise FileNotFoundError(f"No .gguf file found in {directory}")


def build_prompt(user_prompt: str) -> str:
    policies_json = json.dumps(ROUTE_POLICIES)
    conversation_json = json.dumps([{"role": "user", "content": user_prompt}])
    return f"""You are a routing assistant. Given the route policies and user message, select the best matching route.

<route_policies>
{policies_json}
</route_policies>

<conversation>
{conversation_json}
</conversation>

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


def run_benchmark(model: Llama, data: list[dict], label: str) -> dict:
    results = {"correct": 0, "total": 0, "latencies_ms": [], "by_tier": {}, "misclassifications": []}

    # Warmup
    model.create_chat_completion(
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10, temperature=0,
    )

    for i, item in enumerate(data):
        prompt = build_prompt(item["prompt"])

        start = time.perf_counter()
        output = model.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        response = output["choices"][0]["message"]["content"]
        predicted = extract_route(response)
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
            })

        status = "✓" if correct else "✗"
        print(f"  [{i+1:2d}/{len(data)}] {status} [{expected:>7s}→{str(predicted):<7s}] {elapsed_ms:6.1f}ms | {item['prompt'][:55]}")

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
    with open(EVAL_PATH) as f:
        data = json.load(f)
    print(f"Loaded {len(data)} eval prompts\n")

    # ── Stock GGUF ──
    print(f"Loading stock GGUF: {STOCK_GGUF.name}")
    stock_model = Llama(
        model_path=str(STOCK_GGUF),
        n_ctx=512,
        n_gpu_layers=-1,  # All layers on GPU
        verbose=False,
    )
    print("Stock GGUF loaded\n")

    print("Running stock GGUF benchmark...")
    stock_results = run_benchmark(stock_model, data, "Stock GGUF")
    stock_stats = print_results(stock_results, "STOCK Arch-Router-1.5B (GGUF Q8_0)")

    del stock_model

    # ── No-CoT GGUF ──
    print(f"Loading no-CoT GGUF: {NOCOT_GGUF.name}")
    nocot_model = Llama(
        model_path=str(NOCOT_GGUF),
        n_ctx=512,
        n_gpu_layers=-1,
        verbose=False,
    )
    print("No-CoT GGUF loaded\n")

    print("Running no-CoT GGUF benchmark...")
    nocot_results = run_benchmark(nocot_model, data, "No-CoT GGUF")
    nocot_stats = print_results(nocot_results, "GRPO No-CoT Fine-Tuned (GGUF Q8_0)")

    # ── Comparison ──
    print(f"{'='*65}")
    print(f"  GGUF Q8_0 COMPARISON: Stock vs No-CoT Fine-Tuned")
    print(f"{'='*65}")
    print(f"  {'':20s} {'Stock':>12s} {'No-CoT FT':>12s} {'Delta':>10s}")
    print(f"  {'Accuracy':20s} {stock_stats['accuracy']:>11.1f}% {nocot_stats['accuracy']:>11.1f}% {nocot_stats['accuracy']-stock_stats['accuracy']:>+9.1f}%")
    print(f"  {'Avg latency':20s} {stock_stats['avg_ms']:>10.1f}ms {nocot_stats['avg_ms']:>10.1f}ms {nocot_stats['avg_ms']-stock_stats['avg_ms']:>+8.1f}ms")
    print(f"  {'P50 latency':20s} {stock_stats['p50_ms']:>10.1f}ms {nocot_stats['p50_ms']:>10.1f}ms {nocot_stats['p50_ms']-stock_stats['p50_ms']:>+8.1f}ms")
    print(f"  {'P95 latency':20s} {stock_stats['p95_ms']:>10.1f}ms {nocot_stats['p95_ms']:>10.1f}ms {nocot_stats['p95_ms']-stock_stats['p95_ms']:>+8.1f}ms")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
