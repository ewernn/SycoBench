#!/usr/bin/env python3
"""
Test script for new experiment structure
Tests with 2 questions × 2 models to verify everything works
"""

from src.core.sycobench import SycoBench
from pathlib import Path

def main():
    # Load test questions
    test_file = Path("data/datasets/test_2q.txt")
    with open(test_file, 'r') as f:
        questions = [line.strip() for line in f if line.strip()]

    print(f"Loaded {len(questions)} test questions")

    # Define models to test (skip Gemini - library not installed yet)
    models = [
        ("claude", "claude-haiku-3-5"),
        ("openai", "gpt-5-nano"),
    ]

    print(f"Testing {len(models)} models: {[m[1] for m in models]}")

    # Initialize benchmark
    bench = SycoBench()

    # Run comparative benchmark
    print("\nStarting comparative benchmark...")
    result = bench.run_comparative_benchmark(
        models=models,
        questions=questions,
        save_results=True,
        pressure_type="false-authority"
    )

    print(f"\n✓ Experiment complete!")
    print(f"Experiment ID: {result['experiment_id']}")
    print(f"Results saved to: {result['experiment_dir']}")

    return result

if __name__ == "__main__":
    main()