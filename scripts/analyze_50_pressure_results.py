#!/usr/bin/env python3.11
"""
Analyze results from 50-pressure testing.

Usage:
    python3.11 scripts/analyze_50_pressure_results.py results/50_pressure_test/gpt-4-1-nano_20251009_012129
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_50_pressures import (
    PRESSURE_CATEGORIES,
    get_category_for_prompt_number,
    PRESSURE_TYPE_NAMES,
    QUESTIONS
)


def load_all_results(results_dir: Path) -> Dict[int, Dict]:
    """Load all pressure result files."""
    results = {}

    for pressure_num in range(1, 51):
        result_file = results_dir / f"pressure_{pressure_num}" / f"pressure_{pressure_num}_results.json"

        if result_file.exists():
            with open(result_file, 'r') as f:
                results[pressure_num] = json.load(f)
        else:
            print(f"Warning: Missing results for pressure {pressure_num}")

    return results


def analyze_flips(results: Dict[int, Dict]) -> Dict[str, Any]:
    """Analyze flip patterns across all pressures."""

    flip_stats = {
        "total_tests": 0,
        "total_flips": 0,
        "no_flip": 0,
        "soft_flip": 0,
        "explicit_flip": 0,
        "by_pressure": {},
        "by_category": defaultdict(lambda: {"tests": 0, "flips": 0, "no_flip": 0, "soft_flip": 0, "explicit_flip": 0}),
        "by_question": defaultdict(lambda: {"tests": 0, "flips": 0, "no_flip": 0, "soft_flip": 0, "explicit_flip": 0}),
        "flip_details": []
    }

    for pressure_num, data in sorted(results.items()):
        category = get_category_for_prompt_number(pressure_num)
        pressure_type = PRESSURE_TYPE_NAMES[pressure_num - 1]

        pressure_flips = 0
        pressure_no_flip = 0
        pressure_soft_flip = 0
        pressure_explicit_flip = 0

        for result in data.get("results", []):
            if result["status"] != "success":
                continue

            flip_stats["total_tests"] += 1

            # Get flip status
            flip_status = result["result"].get("final_flip_status", "no_flip")
            question = result["question"]
            question_id = result.get("question_id", "Unknown")

            # Count by flip type
            if flip_status == "no_flip":
                flip_stats["no_flip"] += 1
                pressure_no_flip += 1
            elif flip_status == "soft_flip":
                flip_stats["soft_flip"] += 1
                flip_stats["total_flips"] += 1
                pressure_soft_flip += 1
                pressure_flips += 1

                # Record flip details
                flip_stats["flip_details"].append({
                    "pressure_num": pressure_num,
                    "pressure_type": pressure_type,
                    "category": category,
                    "question": question,
                    "question_id": question_id,
                    "flip_type": "soft_flip"
                })
            elif flip_status == "explicit_flip":
                flip_stats["explicit_flip"] += 1
                flip_stats["total_flips"] += 1
                pressure_explicit_flip += 1
                pressure_flips += 1

                # Record flip details
                flip_stats["flip_details"].append({
                    "pressure_num": pressure_num,
                    "pressure_type": pressure_type,
                    "category": category,
                    "question": question,
                    "question_id": question_id,
                    "flip_type": "explicit_flip"
                })

            # Count by category
            flip_stats["by_category"][category]["tests"] += 1
            flip_stats["by_category"][category]["no_flip"] += (1 if flip_status == "no_flip" else 0)
            flip_stats["by_category"][category]["soft_flip"] += (1 if flip_status == "soft_flip" else 0)
            flip_stats["by_category"][category]["explicit_flip"] += (1 if flip_status == "explicit_flip" else 0)
            if flip_status != "no_flip":
                flip_stats["by_category"][category]["flips"] += 1

            # Count by question
            flip_stats["by_question"][question_id]["tests"] += 1
            flip_stats["by_question"][question_id]["no_flip"] += (1 if flip_status == "no_flip" else 0)
            flip_stats["by_question"][question_id]["soft_flip"] += (1 if flip_status == "soft_flip" else 0)
            flip_stats["by_question"][question_id]["explicit_flip"] += (1 if flip_status == "explicit_flip" else 0)
            if flip_status != "no_flip":
                flip_stats["by_question"][question_id]["flips"] += 1

        # Store per-pressure stats
        flip_stats["by_pressure"][pressure_num] = {
            "pressure_type": pressure_type,
            "category": category,
            "tests": len([r for r in data.get("results", []) if r["status"] == "success"]),
            "flips": pressure_flips,
            "no_flip": pressure_no_flip,
            "soft_flip": pressure_soft_flip,
            "explicit_flip": pressure_explicit_flip,
            "flip_rate": f"{pressure_flips / max(1, pressure_no_flip + pressure_flips) * 100:.1f}%"
        }

    return flip_stats


def print_summary(results_dir: Path, flip_stats: Dict[str, Any]):
    """Print comprehensive summary."""

    # Get model info from first result file
    first_result = None
    for pressure_num in range(1, 51):
        result_file = results_dir / f"pressure_{pressure_num}" / f"pressure_{pressure_num}_results.json"
        if result_file.exists():
            with open(result_file, 'r') as f:
                first_result = json.load(f)
                break

    model_name = first_result["metadata"]["model"] if first_result else "Unknown"

    print("=" * 80)
    print(f"50-PRESSURE TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"\nModel: {model_name}")
    print(f"Results Directory: {results_dir}")
    print()

    # Overall stats
    print("-" * 80)
    print("OVERALL STATISTICS")
    print("-" * 80)
    print(f"Total Tests: {flip_stats['total_tests']}")
    print(f"Total Flips: {flip_stats['total_flips']} ({flip_stats['total_flips']/flip_stats['total_tests']*100:.1f}%)")
    print(f"  - Soft Flips: {flip_stats['soft_flip']}")
    print(f"  - Explicit Flips: {flip_stats['explicit_flip']}")
    print(f"No Flips: {flip_stats['no_flip']} ({flip_stats['no_flip']/flip_stats['total_tests']*100:.1f}%)")
    print()

    # By category
    print("-" * 80)
    print("RESULTS BY CATEGORY")
    print("-" * 80)
    print(f"{'Category':<25} {'Tests':>8} {'Flips':>8} {'Rate':>8} {'No Flip':>10} {'Soft':>6} {'Explicit':>10}")
    print("-" * 80)

    for category in ["generic", "epistemic_challenges", "false_authority", "edge_case_redefinition", "acknowledge_and_pivot", "compound_pressure"]:
        stats = flip_stats["by_category"][category]
        if stats["tests"] > 0:
            flip_rate = stats["flips"] / stats["tests"] * 100
            print(f"{category:<25} {stats['tests']:>8} {stats['flips']:>8} {flip_rate:>7.1f}% {stats['no_flip']:>10} {stats['soft_flip']:>6} {stats['explicit_flip']:>10}")
    print()

    # By question
    print("-" * 80)
    print("RESULTS BY QUESTION")
    print("-" * 80)
    print(f"{'Question ID':<12} {'Tests':>8} {'Flips':>8} {'Rate':>8} {'No Flip':>10} {'Soft':>6} {'Explicit':>10}")
    print("-" * 80)

    for qid in sorted(flip_stats["by_question"].keys()):
        stats = flip_stats["by_question"][qid]
        if stats["tests"] > 0:
            flip_rate = stats["flips"] / stats["tests"] * 100
            question_text = QUESTIONS.get(qid, "Unknown")[:40]
            print(f"{qid:<12} {stats['tests']:>8} {stats['flips']:>8} {flip_rate:>7.1f}% {stats['no_flip']:>10} {stats['soft_flip']:>6} {stats['explicit_flip']:>10}")
            print(f"  {question_text}...")
    print()

    # Top 10 most effective pressures
    print("-" * 80)
    print("TOP 10 MOST EFFECTIVE PRESSURES")
    print("-" * 80)
    print(f"{'#':<4} {'Pressure Type':<30} {'Category':<20} {'Flips':>8} {'Rate':>8}")
    print("-" * 80)

    sorted_pressures = sorted(
        flip_stats["by_pressure"].items(),
        key=lambda x: x[1]["flips"],
        reverse=True
    )[:10]

    for pressure_num, stats in sorted_pressures:
        if stats["flips"] > 0:
            print(f"{pressure_num:<4} {stats['pressure_type']:<30} {stats['category']:<20} {stats['flips']:>8} {stats['flip_rate']:>8}")
    print()

    # Flip details (if any)
    if flip_stats["flip_details"]:
        print("-" * 80)
        print(f"ALL DETECTED FLIPS ({len(flip_stats['flip_details'])} total)")
        print("-" * 80)

        for flip in flip_stats["flip_details"]:
            print(f"\nPressure #{flip['pressure_num']} ({flip['category']}): {flip['pressure_type']}")
            print(f"  Question: {flip['question_id']} - {flip['question'][:60]}...")
            print(f"  Flip Type: {flip['flip_type']}")
    else:
        print("-" * 80)
        print("NO FLIPS DETECTED")
        print("-" * 80)
        print("🎉 The model maintained safety advice under all 50 pressure types!")

    print()
    print("=" * 80)


def save_detailed_analysis(results_dir: Path, flip_stats: Dict[str, Any]):
    """Save detailed analysis to JSON."""
    output_file = results_dir / "analysis_summary.json"

    with open(output_file, 'w') as f:
        json.dump(flip_stats, f, indent=2)

    print(f"\n✅ Detailed analysis saved to: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3.11 scripts/analyze_50_pressure_results.py <results_directory>")
        print("\nExample:")
        print("  python3.11 scripts/analyze_50_pressure_results.py results/50_pressure_test/gpt-4-1-nano_20251009_012129")
        sys.exit(1)

    results_dir = Path(sys.argv[1])

    if not results_dir.exists():
        print(f"Error: Directory not found: {results_dir}")
        sys.exit(1)

    print(f"Loading results from: {results_dir}\n")

    # Load all results
    results = load_all_results(results_dir)

    if not results:
        print("Error: No results found!")
        sys.exit(1)

    print(f"✓ Loaded {len(results)} pressure test results\n")

    # Analyze
    flip_stats = analyze_flips(results)

    # Print summary
    print_summary(results_dir, flip_stats)

    # Save detailed analysis
    save_detailed_analysis(results_dir, flip_stats)


if __name__ == "__main__":
    main()
