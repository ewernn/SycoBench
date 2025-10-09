#!/usr/bin/env python3
"""
Create 12 separate graphs showing each model's scores from all 4 judges
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Load the detailed comparison data
with open('results/scorer_comparison_detailed.json') as f:
    data = json.load(f)

model_scores = data['model_scores']

# Define the 4 scorers
scorers = ['gemini-2.5-flash-lite (original)', 'gpt-4.1-nano', 'claude-haiku-3.5', 'grok-4-fast-non-reasoning']
scorer_labels = ['Flash-Lite\n(original)', 'GPT-4.1-nano', 'Claude-Haiku-3.5', 'Grok-4-fast']

# Sort models by company
models_by_company = {
    'Claude': [],
    'Gemini': [],
    'Grok': [],
    'OpenAI': []
}

for model in model_scores.keys():
    if model.startswith('claude_'):
        models_by_company['Claude'].append(model)
    elif model.startswith('gemini_'):
        models_by_company['Gemini'].append(model)
    elif model.startswith('grok_'):
        models_by_company['Grok'].append(model)
    elif model.startswith('openai_'):
        models_by_company['OpenAI'].append(model)

# Sort within each company
for company in models_by_company:
    models_by_company[company].sort()

# Flatten into ordered list
all_models = []
for company in ['Claude', 'Gemini', 'Grok', 'OpenAI']:
    all_models.extend(models_by_company[company])

# Create 12 subplots (3 rows x 4 columns)
fig, axes = plt.subplots(3, 4, figsize=(20, 12))
axes = axes.flatten()

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

for idx, model in enumerate(all_models):
    ax = axes[idx]

    # Get scores for this model
    scores = [model_scores[model][scorer] for scorer in scorers]

    # Create bar chart
    bars = ax.bar(range(4), scores, color=colors, alpha=0.8)

    # Add value labels on bars
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
               f'{score:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

    # Format the model name
    clean_name = model.replace('claude_', '').replace('gemini_', '').replace('grok_', '').replace('openai_', '')

    # Determine company for color coding title
    if model.startswith('claude_'):
        title_color = '#FF6B6B'
    elif model.startswith('gemini_'):
        title_color = '#4ECDC4'
    elif model.startswith('grok_'):
        title_color = '#45B7D1'
    else:
        title_color = '#96CEB4'

    ax.set_title(clean_name, fontsize=11, fontweight='bold', color=title_color, pad=10)
    ax.set_ylim(0, 80)
    ax.set_xticks(range(4))
    ax.set_xticklabels(scorer_labels, fontsize=8, rotation=0)
    ax.set_ylabel('Flip Rate (%)', fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # Add horizontal reference lines
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.3, linewidth=1)
    ax.axhline(y=25, color='orange', linestyle='--', alpha=0.3, linewidth=1)

# Add overall title
fig.suptitle('Flip Rates for All 12 Models Across 4 Different Scorers\nEach graph shows how the 4 scorers evaluated the same model',
             fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout(rect=[0, 0, 1, 0.99])
output_file = 'results/all_12_models_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved 12-model comparison to {output_file}")

# Also create a summary table
print("\n" + "="*100)
print("COMPLETE SCORING MATRIX (48 VALUES)")
print("="*100)

for company in ['Claude', 'Gemini', 'Grok', 'OpenAI']:
    print(f"\n{'='*100}")
    print(f"{company.upper()} MODELS")
    print(f"{'='*100}")
    print(f"{'Model':<35} {'Flash-Lite':>12} {'GPT-4.1-nano':>12} {'Claude-Haiku':>14} {'Grok-4':>12}")
    print("-"*100)

    for model in models_by_company[company]:
        clean_name = model.replace('claude_', '').replace('gemini_', '').replace('grok_', '').replace('openai_', '')
        scores = [model_scores[model][scorer] for scorer in scorers]
        print(f"{clean_name:<35} {scores[0]:>11.1f}% {scores[1]:>11.1f}% {scores[2]:>13.1f}% {scores[3]:>11.1f}%")

print("\n" + "="*100)