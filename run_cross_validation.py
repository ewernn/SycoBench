#!/usr/bin/env python3
"""
Run cross-validation scoring with multiple models.
This script will score each result file with all available scorers.
"""

import subprocess
import json
from pathlib import Path

# Define the scorers to use (deterministic models only)
SCORERS = [
    "gpt-4.1-nano",      # OpenAI - cheapest deterministic ($0.10/$0.40 per 1M)
    "claude-haiku-3.5",  # Anthropic - cheapest ($0.25/$1.25 per 1M)
    "grok-4-fast-non-reasoning",  # xAI - cheapest ($0.05/$0.15 per 1M)
]

# Find all result files to score
result_files = list(Path(".").glob("*results*.json"))
result_files = [f for f in result_files if "rescored" not in f.name and "test_" not in f.name]

if not result_files:
    print("No result files found to score!")
    print("\nTo generate result files, run:")
    print("  python scripts/benchmark_sample.py --questions data/datasets/test_100.txt")
    exit(1)

print(f"Found {len(result_files)} result files to score:")
for f in result_files:
    print(f"  - {f}")

print(f"\nWill use {len(SCORERS)} scorers for cross-validation:")
for scorer in SCORERS:
    print(f"  - {scorer}")

print(f"\nTotal API calls: {len(result_files)} files × {len(SCORERS)} scorers = {len(result_files) * len(SCORERS)} scoring runs")
print("Estimated cost: < $5 total\n")

# Run cross-validation
for result_file in result_files:
    print(f"\n{'='*60}")
    print(f"Scoring: {result_file}")
    print('='*60)

    for scorer in SCORERS:
        output_file = f"rescored_{scorer}_{result_file.stem}.json"
        print(f"\n  Running {scorer}...")

        cmd = [
            "python", "scripts/simple_rescorer.py",
            "--scorer", scorer,
            "--input", str(result_file),
            "--output", output_file
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"  ✅ Saved to {output_file}")
            else:
                print(f"  ❌ Failed: {result.stderr[:200]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

print("\n" + "="*60)
print("Cross-validation complete!")
print("\nTo analyze results, look for agreement rates in the rescored_*.json files")