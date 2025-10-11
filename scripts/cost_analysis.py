#!/usr/bin/env python3
"""
Visualize cost comparison between regular and batch APIs.
"""
import matplotlib.pyplot as plt
import numpy as np

# Data for 1000 questions with pressure testing
models = [
    'GPT-4.1-nano',
    'GPT-4.1-mini', 
    'GPT-4o-mini',
    'Gemini-2.5-flash',
    'Gemini-2.5-pro',
    'Claude-Haiku-3.5'
]

regular_costs = [1.00, 4.00, 1.50, 15.00, 75.00, 5.40]
batch_costs = [0.50, 2.00, 0.75, 0.37, 12.50, 0]  # 0 for Claude (no batch)
batch_available = [True, True, True, True, True, False]

# Create figure with two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Subplot 1: Cost Comparison Bar Chart
x = np.arange(len(models))
width = 0.35

bars1 = ax1.bar(x - width/2, regular_costs, width, label='Regular API', color='#ff6b6b')
bars2 = ax1.bar(x + width/2, batch_costs, width, label='Batch API', color='#4ecdc4')

# Add value labels on bars
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'${height:.2f}', ha='center', va='bottom', fontsize=9)

for i, bar in enumerate(bars2):
    height = bar.get_height()
    if batch_available[i]:
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'${height:.2f}', ha='center', va='bottom', fontsize=9)
    else:
        ax1.text(bar.get_x() + bar.get_width()/2., 0.5,
                 'N/A', ha='center', va='bottom', fontsize=9, style='italic')

ax1.set_xlabel('Model')
ax1.set_ylabel('Cost (USD)')
ax1.set_title('Cost Comparison: 1,000 Questions with Pressure Testing')
ax1.set_xticks(x)
ax1.set_xticklabels(models, rotation=45, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Subplot 2: Savings Percentage
savings_pct = []
for i in range(len(models)):
    if batch_available[i] and regular_costs[i] > 0:
        savings = (regular_costs[i] - batch_costs[i]) / regular_costs[i] * 100
        savings_pct.append(savings)
    else:
        savings_pct.append(0)

colors = ['#4ecdc4' if batch_available[i] else '#cccccc' for i in range(len(models))]
bars3 = ax2.bar(models, savings_pct, color=colors)

# Add percentage labels
for i, bar in enumerate(bars3):
    height = bar.get_height()
    if batch_available[i]:
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_xlabel('Model')
ax2.set_ylabel('Savings (%)')
ax2.set_title('Cost Savings with Batch API')
ax2.set_xticklabels(models, rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3)
ax2.set_ylim(0, 105)

# Add note about time savings
fig.text(0.5, 0.02, 'Note: Batch APIs also save 10-100x time by avoiding rate limits', 
         ha='center', fontsize=10, style='italic')

plt.tight_layout()
plt.savefig('cost_comparison_chart.png', dpi=300, bbox_inches='tight')
print("Cost comparison chart saved to cost_comparison_chart.png")

# Print summary statistics
print("\n=== Summary Statistics ===")
print(f"Average savings (where available): {np.mean([s for s in savings_pct if s > 0]):.1f}%")
print(f"Maximum savings: {max(savings_pct):.1f}% (Gemini-2.5-flash)")
print(f"Total cost regular API: ${sum(regular_costs):.2f}")
print(f"Total cost batch API: ${sum(batch_costs):.2f}")
print(f"Overall savings: ${sum(regular_costs) - sum(batch_costs):.2f}")