#!/usr/bin/env python3
"""
Router Classification Benchmark
================================
Evaluates how accurately the Arch Router (or heuristic fallback) classifies
prompts as simple/medium/complex using real customer support and insurance
claims queries from the actual contract use cases.

Also runs each prompt through the full proxy endpoint to measure:
- Classification accuracy
- Model selection correctness
- Cost savings from routing simple queries to cheap models

Usage:
    # Test classifier only (no API calls)
    python scripts/bench_router.py classify

    # Test full routing through the proxy
    python scripts/bench_router.py route --base-url http://localhost:8000 --customer acme-support

    # Test all customers
    python scripts/bench_router.py route --base-url http://localhost:8000 --all
"""

import argparse
import json
import sys
import time
from pathlib import Path

EVAL_DATA = Path(__file__).parent / "router_eval_data.json"
RESULTS_DIR = Path(__file__).parent.parent / "results"

CHOICES_LABELS = ["A", "B", "C", "D"]

# Cost per million tokens (input, output) from provider_registry.py
MODEL_COSTS = {
    "gpt-4o-mini": (0.15, 0.60),
    "claude-haiku": (0.80, 4.00),
    "gemini-2.0-flash": (0.10, 0.40),
    "gpt-4o": (2.50, 10.00),
    "claude-sonnet": (3.00, 15.00),
    "gemini-2.5-pro": (2.50, 15.00),
    "deepseek-v3": (0.30, 0.80),
}

# What the "expensive baseline" would be — always using the premium model
PREMIUM_MODEL_COST = (3.00, 15.00)  # claude-sonnet tier


def load_eval_data(customer_filter: str | None = None) -> list[dict]:
    with open(EVAL_DATA) as f:
        data = json.load(f)
    if customer_filter:
        data = [d for d in data if d["customer"] == customer_filter]
    return data


def test_heuristic_classifier(data: list[dict]):
    """Test the heuristic classifier against labeled data."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from backend.services.classifier import heuristic_classify

    results = {"correct": 0, "total": 0, "by_tier": {}, "misclassifications": []}

    for item in data:
        predicted = heuristic_classify(item["prompt"])
        expected = item["expected_route"]
        correct = predicted == expected

        results["total"] += 1
        if correct:
            results["correct"] += 1

        # Track per-tier accuracy
        if expected not in results["by_tier"]:
            results["by_tier"][expected] = {"correct": 0, "total": 0}
        results["by_tier"][expected]["total"] += 1
        if correct:
            results["by_tier"][expected]["correct"] += 1

        status = "✓" if correct else "✗"
        if not correct:
            results["misclassifications"].append({
                "prompt": item["prompt"][:80],
                "expected": expected,
                "predicted": predicted,
                "customer": item["customer"],
            })

        print(f"  {status} [{expected:>7s}→{predicted:<7s}] {item['prompt'][:70]}")

    print(f"\n{'='*60}")
    print(f"  HEURISTIC CLASSIFIER RESULTS")
    print(f"{'='*60}")
    for tier in ("simple", "medium", "complex"):
        if tier in results["by_tier"]:
            t = results["by_tier"][tier]
            pct = t["correct"] / t["total"] * 100 if t["total"] else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            print(f"  {tier:<10s} {t['correct']:>2d}/{t['total']:<2d} ({pct:5.1f}%) {bar}")

    total_pct = results["correct"] / results["total"] * 100
    print(f"\n  OVERALL: {results['correct']}/{results['total']} ({total_pct:.1f}%)")

    if results["misclassifications"]:
        print(f"\n  MISCLASSIFICATIONS:")
        for m in results["misclassifications"]:
            print(f"    [{m['customer']}] {m['expected']}→{m['predicted']}: {m['prompt']}")

    print(f"{'='*60}\n")
    return results


def test_full_routing(data: list[dict], base_url: str, customer_id: str):
    """Test full routing through the proxy endpoint."""
    try:
        from openai import OpenAI
    except ImportError:
        print("Install openai: pip install openai")
        sys.exit(1)

    client = OpenAI(base_url=f"{base_url}/v1", api_key="bench")
    results = []

    for i, item in enumerate(data):
        start = time.time()
        try:
            resp = client.chat.completions.create(
                model="auto",
                messages=[{"role": "user", "content": item["prompt"]}],
                max_tokens=512,
                temperature=0,
                extra_headers={"X-Customer-ID": customer_id},
            )
            elapsed_ms = (time.time() - start) * 1000

            # Extract routing headers from raw response
            raw_resp = resp.model_extra or {}
            model_used = resp.model or "unknown"

            usage = resp.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0

            result = {
                "index": i,
                "prompt": item["prompt"][:80],
                "expected_route": item["expected_route"],
                "model_used": model_used,
                "latency_ms": round(elapsed_ms, 1),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "customer": item["customer"],
                "domain": item["domain"],
            }
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            result = {
                "index": i,
                "prompt": item["prompt"][:80],
                "expected_route": item["expected_route"],
                "model_used": "error",
                "latency_ms": round(elapsed_ms, 1),
                "input_tokens": 0,
                "output_tokens": 0,
                "customer": item["customer"],
                "domain": item["domain"],
                "error": str(e),
            }

        tier = item["expected_route"]
        print(f"  [{i+1:2d}/{len(data)}] [{tier:>7s}] {result['model_used']:<20s} {result['latency_ms']:>7.0f}ms | {item['prompt'][:50]}")
        results.append(result)

    # Cost analysis
    print(f"\n{'='*60}")
    print(f"  ROUTING RESULTS — {customer_id}")
    print(f"{'='*60}")

    routed_cost = 0
    premium_cost = 0
    for r in results:
        model = r["model_used"]
        in_tok = r["input_tokens"]
        out_tok = r["output_tokens"]

        # Actual routed cost
        costs = MODEL_COSTS.get(model, PREMIUM_MODEL_COST)
        routed_cost += (in_tok / 1_000_000) * costs[0] + (out_tok / 1_000_000) * costs[1]

        # What it would cost with premium model for everything
        premium_cost += (in_tok / 1_000_000) * PREMIUM_MODEL_COST[0] + (out_tok / 1_000_000) * PREMIUM_MODEL_COST[1]

    savings_pct = (1 - routed_cost / premium_cost) * 100 if premium_cost > 0 else 0

    # Model distribution
    model_counts = {}
    for r in results:
        m = r["model_used"]
        model_counts[m] = model_counts.get(m, 0) + 1

    print(f"\n  Model distribution:")
    for model, count in sorted(model_counts.items(), key=lambda x: -x[1]):
        pct = count / len(results) * 100
        cost_info = MODEL_COSTS.get(model, ("?", "?"))
        print(f"    {model:<25s} {count:>3d} ({pct:5.1f}%) — ${cost_info[0]}/{cost_info[1]} per M tokens")

    print(f"\n  Cost analysis (estimated):")
    print(f"    Routed cost:    ${routed_cost:.6f}")
    print(f"    All-premium:    ${premium_cost:.6f}")
    print(f"    Savings:        {savings_pct:.1f}%")

    avg_latency = sum(r["latency_ms"] for r in results) / len(results) if results else 0
    print(f"\n  Avg latency:      {avg_latency:.0f}ms")
    print(f"{'='*60}\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Router Classification Benchmark")
    sub = parser.add_subparsers(dest="command")

    # Classify subcommand — test heuristic classifier only
    cls_p = sub.add_parser("classify", help="Test heuristic classifier accuracy")
    cls_p.add_argument("--customer", default=None, help="Filter to specific customer")

    # Route subcommand — test full proxy routing
    rt_p = sub.add_parser("route", help="Test full routing through proxy")
    rt_p.add_argument("--base-url", required=True, help="Proxy base URL (e.g., http://localhost:8000)")
    rt_p.add_argument("--customer", default=None, help="Customer ID to test")
    rt_p.add_argument("--all", action="store_true", help="Test all customers")

    args = parser.parse_args()

    if args.command == "classify":
        data = load_eval_data(args.customer)
        print(f"\nRouter Classification Benchmark — {len(data)} prompts")
        if args.customer:
            print(f"  Filtered to: {args.customer}")
        print()
        test_heuristic_classifier(data)

    elif args.command == "route":
        if args.all:
            for cust in ["acme-support", "globex-claims", "samsung-care"]:
                data = load_eval_data(cust)
                if data:
                    print(f"\n{'#'*60}")
                    print(f"  Testing customer: {cust} ({len(data)} prompts)")
                    print(f"{'#'*60}\n")
                    test_full_routing(data, args.base_url, cust)
        elif args.customer:
            data = load_eval_data(args.customer)
            test_full_routing(data, args.base_url, args.customer)
        else:
            data = load_eval_data()
            test_full_routing(data, args.base_url, "acme-support")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
