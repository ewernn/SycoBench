#!/usr/bin/env python3
"""
Compare what each scorer actually found (not just agreement)
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load all scorer results
scorers = ['gpt-4.1-nano', 'claude-haiku-3.5', 'grok-4-fast-non-reasoning']
scorer_data = {}

for scorer in scorers:
    scorer_files = list(Path('results').glob(f'{scorer}_scores_*.json'))
    scorer_data[scorer] = {}

    print(f"\nProcessing scorer: {scorer}")
    for file in scorer_files:
        print(f"  Loading {file.name}...")
        with open(file) as f:
            data = json.load(f)
            for model, results in data['rescored_results'].items():
                total = len(results)
                flips = sum(1 for r in results if r['rescored'] in ['explicit_flip', 'soft_flip'])
                scorer_data[scorer][model] = (flips / total * 100) if total > 0 else 0

    print(f"  Found {len(scorer_data[scorer])} models")

# Add Flash-Lite original scores (extracted from ALL scorer files)
print("\nExtracting Flash-Lite original scores from ALL results...")
flash_lite_scores = {}
all_scorer_files = list(Path('results').glob('*_scores_*.json'))
for file in all_scorer_files:
    with open(file) as f:
        data = json.load(f)
        for model, results in data['rescored_results'].items():
            if model not in flash_lite_scores:  # Only add once
                total = len(results)
                original_flips = sum(1 for r in results if r['original'] in ['explicit_flip', 'soft_flip'])
                flash_lite_scores[model] = (original_flips / total * 100) if total > 0 else 0

scorer_data['gemini-2.5-flash-lite (original)'] = flash_lite_scores
print(f"Found {len(flash_lite_scores)} models in Flash-Lite original scores")

# Create grouped bar chart
models = sorted(flash_lite_scores.keys())
clean_model_names = [m.replace('claude_', '').replace('gemini_', '').replace('grok_', '').replace('openai_', '') for m in models]

fig, ax = plt.subplots(figsize=(18, 10))

x = np.arange(len(models))
width = 0.2
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

scorers_list = ['gemini-2.5-flash-lite (original)', 'gpt-4.1-nano', 'claude-haiku-3.5', 'grok-4-fast-non-reasoning']

for i, (scorer, color) in enumerate(zip(scorers_list, colors)):
    values = [scorer_data[scorer].get(model, 0) for model in models]
    offset = width * (i - 1.5)
    bars = ax.bar(x + offset, values, width, label=scorer, color=color, alpha=0.8)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{val:.0f}', ha='center', va='bottom', fontsize=7)

ax.set_xlabel('Model', fontsize=12, fontweight='bold')
ax.set_ylabel('Flip Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('Model Flip Rates by Different Scorers\nShowing how each scorer evaluated the same responses', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(clean_model_names, rotation=45, ha='right', fontsize=9)
ax.legend(title='Scorer Model', loc='upper left', fontsize=10)
ax.grid(axis='y', alpha=0.3)

# Add horizontal lines for reference
ax.axhline(y=50, color='red', linestyle='--', alpha=0.3, linewidth=1)
ax.axhline(y=25, color='orange', linestyle='--', alpha=0.3, linewidth=1)

plt.tight_layout()
output_file = 'results/scorer_comparison_flip_rates.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Saved chart to {output_file}")

# Print summary statistics
print("\n" + "="*80)
print("SCORER COMPARISON SUMMARY")
print("="*80)

print("\nAverage flip rate by scorer across all models:")
for scorer in scorers_list:
    avg_flip = np.mean(list(scorer_data[scorer].values()))
    print(f"{scorer:40} {avg_flip:5.1f}%")

print("\nMost controversial models (highest variance between scorers):")
variances = []
for model in models:
    scores = [scorer_data[s].get(model, 0) for s in scorers_list]
    variance = np.var(scores)
    std_dev = np.std(scores)
    variances.append((model, variance, std_dev, scores))

for model, var, std, scores in sorted(variances, key=lambda x: x[1], reverse=True)[:8]:
    clean_name = model.replace('claude_', '').replace('gemini_', '').replace('grok_', '').replace('openai_', '')
    print(f"\n{clean_name}:")
    print(f"  Standard deviation: {std:.1f}")
    print(f"  Scores: {', '.join([f'{s:.1f}%' for s in scores])}")
    print(f"  Range: {min(scores):.1f}% to {max(scores):.1f}% (diff: {max(scores)-min(scores):.1f}%)")

print("\n" + "="*80)
print("SAFEST MODELS (lowest average flip rate across all scorers)")
print("="*80)

avg_by_model = []
for model in models:
    scores = [scorer_data[s].get(model, 0) for s in scorers_list]
    avg = np.mean(scores)
    avg_by_model.append((model, avg, scores))

for model, avg, scores in sorted(avg_by_model, key=lambda x: x[1])[:5]:
    clean_name = model.replace('claude_', '').replace('gemini_', '').replace('grok_', '').replace('openai_', '')
    print(f"{clean_name:30} {avg:5.1f}% avg flip rate")

print("\n" + "="*80)
print("MOST SYCOPHANTIC MODELS (highest average flip rate)")
print("="*80)

for model, avg, scores in sorted(avg_by_model, key=lambda x: x[1], reverse=True)[:5]:
    clean_name = model.replace('claude_', '').replace('gemini_', '').replace('grok_', '').replace('openai_', '')
    print(f"{clean_name:30} {avg:5.1f}% avg flip rate")

print("\n" + "="*80)

# Save detailed comparison to JSON
comparison_output = {
    "scorer_averages": {scorer: float(np.mean(list(scorer_data[scorer].values()))) for scorer in scorers_list},
    "model_scores": {model: {scorer: float(scorer_data[scorer].get(model, 0)) for scorer in scorers_list} for model in models},
    "model_statistics": {
        model: {
            "average": float(np.mean([scorer_data[s].get(model, 0) for s in scorers_list])),
            "std_dev": float(np.std([scorer_data[s].get(model, 0) for s in scorers_list])),
            "min": float(min([scorer_data[s].get(model, 0) for s in scorers_list])),
            "max": float(max([scorer_data[s].get(model, 0) for s in scorers_list]))
        } for model in models
    }
}

json_output = 'results/scorer_comparison_detailed.json'
with open(json_output, 'w') as f:
    json.dump(comparison_output, f, indent=2)
print(f"✓ Saved detailed comparison to {json_output}")