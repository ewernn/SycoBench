#!/usr/bin/env python3
"""
Analyze cross-validation results from multiple scorers.
"""

import json
from pathlib import Path
from collections import defaultdict

# Load all rescored files
rescored_files = list(Path(".").glob("rescored_*_benchmark.json"))

if not rescored_files:
    print("No rescored files found!")
    exit(1)

print("CROSS-VALIDATION ANALYSIS")
print("=" * 60)
print(f"Found {len(rescored_files)} rescored files")

# Collect all scores
all_scores = defaultdict(lambda: defaultdict(list))
scorer_names = []

for file in rescored_files:
    with open(file) as f:
        data = json.load(f)

    scorer = data["scorer"]
    scorer_names.append(scorer)

    for model_key, rescores in data["rescored_results"].items():
        for rescore in rescores:
            key = (model_key, rescore["question_num"], rescore["pressure_level"])
            all_scores[key][scorer] = rescore["rescored"]

print(f"\nScorers used:")
for scorer in scorer_names:
    print(f"  - {scorer}")

# Analyze agreement
print("\n" + "=" * 60)
print("INTER-RATER AGREEMENT ANALYSIS")
print("=" * 60)

total_evaluations = len(all_scores)
perfect_agreement = 0
majority_agreement = 0
disagreements = []

for key, scores in all_scores.items():
    model, q_num, p_level = key
    scorer_decisions = list(scores.values())

    # Check perfect agreement
    if len(set(scorer_decisions)) == 1:
        perfect_agreement += 1

    # Check majority agreement (2+ out of 3)
    for decision in set(scorer_decisions):
        if scorer_decisions.count(decision) >= 2:
            majority_agreement += 1
            break

    # Track disagreements
    if len(set(scorer_decisions)) > 1:
        disagreements.append({
            "model": model,
            "question": q_num,
            "pressure_level": p_level,
            "scores": scores
        })

print(f"\nTotal evaluations: {total_evaluations}")
print(f"Perfect agreement (all 3 scorers): {perfect_agreement}/{total_evaluations} ({perfect_agreement/total_evaluations*100:.1f}%)")
print(f"Majority agreement (2+ scorers): {majority_agreement}/{total_evaluations} ({majority_agreement/total_evaluations*100:.1f}%)")

# Show disagreements
if disagreements:
    print(f"\n{len(disagreements)} cases with disagreement:")
    for i, d in enumerate(disagreements[:5], 1):  # Show first 5
        print(f"\n  {i}. {d['model']} - Q{d['question']}, Level {d['pressure_level']}:")
        for scorer, decision in d['scores'].items():
            print(f"     {scorer}: {decision}")

# Model-specific analysis
print("\n" + "=" * 60)
print("MODEL-SPECIFIC FLIP RATES")
print("=" * 60)

model_flip_rates = defaultdict(lambda: defaultdict(int))
for key, scores in all_scores.items():
    model = key[0]
    for scorer, decision in scores.items():
        if decision in ["explicit_flip", "soft_flip"]:
            model_flip_rates[model][scorer] += 1

for model in sorted(model_flip_rates.keys()):
    print(f"\n{model}:")
    for scorer in scorer_names:
        flips = model_flip_rates[model][scorer]
        total = sum(1 for k in all_scores if k[0] == model)
        print(f"  {scorer}: {flips}/{total} flips ({flips/total*100:.1f}%)")

# Scorer consistency
print("\n" + "=" * 60)
print("SCORER TENDENCIES")
print("=" * 60)

scorer_stats = defaultdict(lambda: {"explicit": 0, "soft": 0, "no_flip": 0, "total": 0})
for scores in all_scores.values():
    for scorer, decision in scores.items():
        if decision == "explicit_flip":
            scorer_stats[scorer]["explicit"] += 1
        elif decision == "soft_flip":
            scorer_stats[scorer]["soft"] += 1
        elif decision == "no_flip":
            scorer_stats[scorer]["no_flip"] += 1
        scorer_stats[scorer]["total"] += 1

for scorer in scorer_names:
    stats = scorer_stats[scorer]
    if stats["total"] > 0:
        print(f"\n{scorer}:")
        print(f"  Explicit flips: {stats['explicit']}/{stats['total']} ({stats['explicit']/stats['total']*100:.1f}%)")
        print(f"  Soft flips: {stats['soft']}/{stats['total']} ({stats['soft']/stats['total']*100:.1f}%)")
        print(f"  No flips: {stats['no_flip']}/{stats['total']} ({stats['no_flip']/stats['total']*100:.1f}%)")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"✅ Cross-validation complete with {len(scorer_names)} independent scorers")
print(f"📊 Inter-rater reliability: {perfect_agreement/total_evaluations*100:.1f}% perfect agreement")
print(f"🎯 Majority consensus: {majority_agreement/total_evaluations*100:.1f}% of evaluations")

if perfect_agreement/total_evaluations > 0.7:
    print("✨ High inter-rater reliability - results are well-validated")
elif perfect_agreement/total_evaluations > 0.5:
    print("👍 Moderate inter-rater reliability - results show good consistency")
else:
    print("⚠️ Low inter-rater reliability - consider reviewing scoring criteria")