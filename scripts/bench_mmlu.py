#!/usr/bin/env python3
"""
MMLU Benchmark Runner
=====================
Runs a fixed set of MMLU questions against any OpenAI-compatible API.
Switch the base URL to compare your router vs direct model access.

Usage:
    # Direct to Groq
    python scripts/bench_mmlu.py --base-url https://api.groq.com/openai/v1 --api-key $GROQ_API_KEY --model llama-3.3-70b-versatile

    # Through your router
    python scripts/bench_mmlu.py --base-url http://localhost:8000/v1 --api-key dummy --model auto

    # Compare two runs
    python scripts/bench_mmlu.py --compare results/direct.json results/router.json
"""

import argparse
import json
import time
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Install openai: pip install openai")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Load real MMLU questions from HuggingFace (cais/mmlu) — pulled by:
#   datasets lib → scripts/mmlu_questions.json
# 60 questions: 10 each from 6 subjects (3 easy, 1 medium, 2 hard)
# ---------------------------------------------------------------------------
QUESTIONS_FILE = Path(__file__).parent / "mmlu_questions.json"

def load_questions() -> list[tuple[str, str, list[str], int]]:
    with open(QUESTIONS_FILE) as f:
        raw = json.load(f)
    return [(q["subject"], q["question"], q["choices"], q["answer"]) for q in raw]

MMLU_QUESTIONS = load_questions()

CHOICES_LABELS = ["A", "B", "C", "D"]

RESULTS_DIR = Path(__file__).parent.parent / "results"


def format_prompt(subject: str, question: str, choices: list[str]) -> str:
    """Format an MMLU question as a prompt."""
    choices_text = "\n".join(f"{CHOICES_LABELS[i]}. {c}" for i, c in enumerate(choices))
    return (
        f"The following is a multiple choice question about {subject.replace('_', ' ')}.\n\n"
        f"{question}\n{choices_text}\n\n"
        f"Answer with just the letter (A, B, C, or D)."
    )


def extract_answer(response_text: str) -> str | None:
    """Extract the answer letter from model response."""
    text = response_text.strip().upper()
    # Check first character
    if text and text[0] in CHOICES_LABELS:
        return text[0]
    # Search for a standalone letter
    for ch in CHOICES_LABELS:
        if ch in text:
            return ch
    return None


def run_benchmark(client: OpenAI, model: str, reasoning_effort: str | None = None) -> list[dict]:
    """Run all MMLU questions and return results."""
    results = []
    total = len(MMLU_QUESTIONS)

    for i, (subject, question, choices, correct_idx) in enumerate(MMLU_QUESTIONS):
        prompt = format_prompt(subject, question, choices)
        correct_letter = CHOICES_LABELS[correct_idx]

        start = time.time()
        try:
            kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4096,
                "temperature": 0,
            }
            if reasoning_effort:
                kwargs["extra_body"] = {"reasoning": {"effort": reasoning_effort}}
            resp = client.chat.completions.create(**kwargs)
            elapsed_ms = (time.time() - start) * 1000
            raw = resp.choices[0].message.content or ""
            answer = extract_answer(raw)
            is_correct = answer == correct_letter

            usage = resp.usage
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0

            result = {
                "index": i,
                "subject": subject,
                "question": question,
                "correct_answer": correct_letter,
                "model_answer": answer,
                "model_raw": raw.strip(),
                "correct": is_correct,
                "latency_ms": round(elapsed_ms, 1),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model_used": resp.model if resp.model else model,
            }
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            result = {
                "index": i,
                "subject": subject,
                "question": question,
                "correct_answer": correct_letter,
                "model_answer": None,
                "model_raw": str(e),
                "correct": False,
                "latency_ms": round(elapsed_ms, 1),
                "input_tokens": 0,
                "output_tokens": 0,
                "model_used": model,
            }

        status = "✓" if result["correct"] else "✗"
        print(f"  [{i+1:2d}/{total}] {status} {subject[:25]:<25s} | {result['model_raw'][:20]:<20s} | {result['latency_ms']:>7.0f}ms")
        results.append(result)

    return results


def print_summary(results: list[dict], label: str):
    """Print accuracy breakdown by subject."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")

    # By subject
    subjects = {}
    for r in results:
        subj = r["subject"]
        if subj not in subjects:
            subjects[subj] = {"correct": 0, "total": 0}
        subjects[subj]["total"] += 1
        if r["correct"]:
            subjects[subj]["correct"] += 1

    # Group into easy/hard
    easy_subjects = {"elementary_mathematics", "high_school_us_history", "high_school_computer_science"}
    hard_subjects = {"abstract_algebra", "formal_logic"}

    easy_correct = sum(s["correct"] for k, s in subjects.items() if k in easy_subjects)
    easy_total = sum(s["total"] for k, s in subjects.items() if k in easy_subjects)
    hard_correct = sum(s["correct"] for k, s in subjects.items() if k in hard_subjects)
    hard_total = sum(s["total"] for k, s in subjects.items() if k in hard_subjects)

    for subj, stats in sorted(subjects.items()):
        pct = stats["correct"] / stats["total"] * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        difficulty = "EASY" if subj in easy_subjects else ("HARD" if subj in hard_subjects else "MED ")
        print(f"  [{difficulty}] {subj:<30s} {stats['correct']:>2d}/{stats['total']:<2d} ({pct:5.1f}%) {bar}")

    total_correct = sum(1 for r in results if r["correct"])
    total = len(results)
    total_input = sum(r["input_tokens"] for r in results)
    total_output = sum(r["output_tokens"] for r in results)
    avg_latency = sum(r["latency_ms"] for r in results) / len(results) if results else 0

    print(f"\n  EASY accuracy:   {easy_correct}/{easy_total} ({easy_correct/easy_total*100:.1f}%)" if easy_total else "")
    print(f"  HARD accuracy:   {hard_correct}/{hard_total} ({hard_correct/hard_total*100:.1f}%)" if hard_total else "")
    print(f"  OVERALL:         {total_correct}/{total} ({total_correct/total*100:.1f}%)")
    print(f"  Total tokens:    {total_input} in / {total_output} out")
    print(f"  Avg latency:     {avg_latency:.0f}ms")
    print(f"{'='*60}\n")


def compare_results(file_a: str, file_b: str):
    """Compare two saved result files."""
    with open(file_a) as f:
        data_a = json.load(f)
    with open(file_b) as f:
        data_b = json.load(f)

    label_a = data_a.get("label", file_a)
    label_b = data_b.get("label", file_b)

    print_summary(data_a["results"], label_a)
    print_summary(data_b["results"], label_b)

    # Cost comparison
    tokens_a_in = sum(r["input_tokens"] for r in data_a["results"])
    tokens_a_out = sum(r["output_tokens"] for r in data_a["results"])
    tokens_b_in = sum(r["input_tokens"] for r in data_b["results"])
    tokens_b_out = sum(r["output_tokens"] for r in data_b["results"])

    acc_a = sum(1 for r in data_a["results"] if r["correct"]) / len(data_a["results"]) * 100
    acc_b = sum(1 for r in data_b["results"] if r["correct"]) / len(data_b["results"]) * 100

    print(f"  COMPARISON")
    print(f"  {'':30s} {'A':>12s} {'B':>12s}")
    print(f"  {'Label':30s} {label_a:>12s} {label_b:>12s}")
    print(f"  {'Accuracy':30s} {acc_a:>11.1f}% {acc_b:>11.1f}%")
    print(f"  {'Input tokens':30s} {tokens_a_in:>12,d} {tokens_b_in:>12,d}")
    print(f"  {'Output tokens':30s} {tokens_a_out:>12,d} {tokens_b_out:>12,d}")

    latency_a = sum(r["latency_ms"] for r in data_a["results"]) / len(data_a["results"])
    latency_b = sum(r["latency_ms"] for r in data_b["results"]) / len(data_b["results"])
    print(f"  {'Avg latency':30s} {latency_a:>10.0f}ms {latency_b:>10.0f}ms")


def main():
    parser = argparse.ArgumentParser(description="MMLU Benchmark Runner")
    sub = parser.add_subparsers(dest="command")

    # Run subcommand
    run_p = sub.add_parser("run", help="Run the benchmark")
    run_p.add_argument("--base-url", required=True, help="OpenAI-compatible API base URL")
    run_p.add_argument("--api-key", required=True, help="API key")
    run_p.add_argument("--model", required=True, help="Model name to request")
    run_p.add_argument("--label", default=None, help="Label for this run (used in output)")
    run_p.add_argument("--output", "-o", default=None, help="Output JSON file path")
    run_p.add_argument("--reasoning-effort", default=None, choices=["low", "medium", "high"], help="Reasoning effort for reasoning models")

    # Compare subcommand
    cmp_p = sub.add_parser("compare", help="Compare two result files")
    cmp_p.add_argument("file_a", help="First results JSON")
    cmp_p.add_argument("file_b", help="Second results JSON")

    args = parser.parse_args()

    if args.command == "compare":
        compare_results(args.file_a, args.file_b)
        return

    if args.command != "run":
        parser.print_help()
        return

    label = args.label or f"{args.model}@{args.base_url.split('//')[1].split('/')[0] if '//' in args.base_url else args.base_url}"

    print(f"\nMMLU Benchmark — {label}")
    print(f"  Model: {args.model}")
    print(f"  URL:   {args.base_url}")
    print(f"  Questions: {len(MMLU_QUESTIONS)}\n")

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    results = run_benchmark(client, args.model, reasoning_effort=args.reasoning_effort)
    print_summary(results, label)

    # Save results
    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = args.output or str(RESULTS_DIR / f"mmlu_{label.replace('/', '_').replace(':', '_')}.json")
    output = {
        "label": label,
        "model": args.model,
        "base_url": args.base_url,
        "num_questions": len(MMLU_QUESTIONS),
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved to {out_path}")


if __name__ == "__main__":
    main()
