#!/usr/bin/env python3
"""Extract summaries from all scorer result files"""
import json
import glob
from pathlib import Path

# Find all scorer result files
scorer_files = glob.glob("results/*_scores_*.json")

if not scorer_files:
    print("No scorer files found!")
    exit(1)

print(f"Found {len(scorer_files)} scorer result files")

# Group results by scorer
results_by_scorer = {}
results_by_model = {}

for file in scorer_files:
    print(f"Processing {file}...")
    with open(file) as f:
        data = json.load(f)

    scorer = data["scorer"]

    if scorer not in results_by_scorer:
        results_by_scorer[scorer] = {}

    # Calculate summaries for each model in this file
    for model_key, rescores in data["rescored_results"].items():
        agreements = sum(1 for r in rescores if r["agrees"])
        total = len(rescores)
        agreement_rate = (agreements / total * 100) if total > 0 else 0

        # Count flips by new scorer
        explicit_flips = sum(1 for r in rescores if r["rescored"] == "explicit_flip")
        soft_flips = sum(1 for r in rescores if r["rescored"] == "soft_flip")
        total_flips = explicit_flips + soft_flips
        flip_rate = (total_flips / total * 100) if total > 0 else 0

        # Count original flips (Flash-Lite's opinion)
        original_flips = sum(1 for r in rescores if r["original"] in ["explicit_flip", "soft_flip"])
        original_flip_rate = (original_flips / total * 100) if total > 0 else 0

        results_by_scorer[scorer][model_key] = {
            "agreement_rate": agreement_rate,
            "new_flip_rate": flip_rate,
            "original_flip_rate": original_flip_rate,
            "explicit_flips": explicit_flips,
            "soft_flips": soft_flips,
            "total": total
        }

        # Also group by model
        if model_key not in results_by_model:
            results_by_model[model_key] = {}
        results_by_model[model_key][scorer] = {
            "agreement": agreement_rate,
            "flip_rate": flip_rate,
            "original_flip_rate": original_flip_rate
        }

# Build output text
output_lines = []
output_lines.append("=" * 80)
output_lines.append("RESULTS BY SCORER")
output_lines.append("=" * 80)

for scorer, models in sorted(results_by_scorer.items()):
    output_lines.append(f"\n{scorer} Scoring Results:")
    output_lines.append("-" * 50)
    for model, stats in sorted(models.items()):
        line = (f"{model:40} Agreement: {stats['agreement_rate']:5.1f}% | "
                f"Flips: {stats['new_flip_rate']:5.1f}% "
                f"(Flash-Lite said {stats['original_flip_rate']:5.1f}%)")
        output_lines.append(line)

# Print results by model
output_lines.append("\n" + "=" * 80)
output_lines.append("RESULTS BY MODEL (how different scorers see each model)")
output_lines.append("=" * 80)

for model, scorers in sorted(results_by_model.items()):
    output_lines.append(f"\n{model}:")
    output_lines.append("-" * 50)
    for scorer, stats in sorted(scorers.items()):
        line = (f"  {scorer:30} Agreement: {stats['agreement']:5.1f}% | "
                f"Flip rate: {stats['flip_rate']:5.1f}% "
                f"(Flash-Lite: {stats['original_flip_rate']:5.1f}%)")
        output_lines.append(line)

# Calculate overall agreement
output_lines.append("\n" + "=" * 80)
output_lines.append("OVERALL SCORER AGREEMENT WITH FLASH-LITE")
output_lines.append("=" * 80)

total_agreements = 0
total_comparisons = 0

for scorer, models in results_by_scorer.items():
    for model, stats in models.items():
        total_agreements += stats["agreement_rate"] * stats["total"] / 100
        total_comparisons += stats["total"]

overall_agreement = (total_agreements / total_comparisons * 100) if total_comparisons > 0 else 0
output_lines.append(f"Overall agreement across all scorers: {overall_agreement:.1f}%")
output_lines.append(f"Total comparisons: {int(total_comparisons)}")

# Per-scorer agreement summary
output_lines.append("\nAgreement by scorer:")
for scorer, models in sorted(results_by_scorer.items()):
    scorer_agreements = 0
    scorer_total = 0
    for model, stats in models.items():
        scorer_agreements += stats["agreement_rate"] * stats["total"] / 100
        scorer_total += stats["total"]
    scorer_agreement = (scorer_agreements / scorer_total * 100) if scorer_total > 0 else 0
    output_lines.append(f"  {scorer:30} {scorer_agreement:5.1f}% agreement")

# Find controversial models (high disagreement)
output_lines.append("\n" + "=" * 80)
output_lines.append("MOST CONTROVERSIAL MODELS (lowest agreement)")
output_lines.append("=" * 80)
controversial = []
for model, scorers in results_by_model.items():
    avg_agreement = sum(s["agreement"] for s in scorers.values()) / len(scorers)
    controversial.append((model, avg_agreement))

for model, avg in sorted(controversial, key=lambda x: x[1])[:10]:
    output_lines.append(f"  {model:40} {avg:.1f}% average agreement")

output_lines.append("\n" + "=" * 80)
output_lines.append("HIGHEST AGREEMENT MODELS")
output_lines.append("=" * 80)
for model, avg in sorted(controversial, key=lambda x: x[1], reverse=True)[:10]:
    output_lines.append(f"  {model:40} {avg:.1f}% average agreement")

# Print to console
output_text = "\n".join(output_lines)
print("\n" + output_text)

# Save to files
output_file = "results/scorer_analysis_summary.txt"
with open(output_file, 'w') as f:
    f.write(output_text)
print(f"\n✓ Saved summary to {output_file}")

# Save detailed JSON
json_output = {
    "by_scorer": results_by_scorer,
    "by_model": results_by_model,
    "overall_agreement": overall_agreement,
    "total_comparisons": int(total_comparisons)
}

json_file = "results/scorer_analysis_detailed.json"
with open(json_file, 'w') as f:
    json.dump(json_output, f, indent=2)
print(f"✓ Saved detailed JSON to {json_file}")