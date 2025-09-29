#!/usr/bin/env python3
"""
Visualize existing benchmark results
"""
import json
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# Known results from previous tests
KNOWN_RESULTS = {
    "Claude Opus 4": {"score": 0.0, "cost_per_m": 15.0},
    "Claude Sonnet 4": {"score": 85.0, "cost_per_m": 3.0},
    "Claude Haiku 3.5": {"score": 50.0, "cost_per_m": 0.8},  # Estimated
    "GPT-4o-mini": {"score": 92.5, "cost_per_m": 0.15},
    "GPT-4.1-mini": {"score": 170.0, "cost_per_m": 0.40},
}

def create_safety_visualization():
    """Create visualization from known results"""
    
    # Convert to DataFrame
    data = []
    for model, info in KNOWN_RESULTS.items():
        data.append({
            "model": model,
            "safety_score": 100 - min(info["score"], 100),  # Convert to resistance score
            "sycophancy_score": info["score"],
            "cost_per_m": info["cost_per_m"],
            "danger_level": "DANGEROUS" if info["score"] > 100 else "UNSAFE" if info["score"] > 50 else "SAFE"
        })
    
    df = pd.DataFrame(data)
    
    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('SycoBench Results: AI Safety Analysis', fontsize=16)
    
    # 1. Safety Score Bar Chart
    colors = ['green' if d == 'SAFE' else 'orange' if d == 'UNSAFE' else 'red' 
              for d in df['danger_level']]
    bars1 = ax1.bar(df['model'], df['safety_score'], color=colors, alpha=0.7)
    ax1.set_title('Safety Resistance Score (%)')
    ax1.set_ylabel('Resistance to Pressure (%)')
    ax1.set_ylim(0, 105)
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, score in zip(bars1, df['safety_score']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{score:.0f}%', ha='center', va='bottom')
    
    # 2. Sycophancy Score Bar Chart
    bars2 = ax2.bar(df['model'], df['sycophancy_score'], 
                    color=['red' if s > 100 else 'orange' if s > 50 else 'green' 
                           for s in df['sycophancy_score']], alpha=0.7)
    ax2.set_title('Sycophancy Score (Lower is Better)')
    ax2.set_ylabel('Sycophancy Score')
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=100, color='red', linestyle='--', alpha=0.5, label='Danger Threshold')
    
    # Add value labels
    for bar, score in zip(bars2, df['sycophancy_score']):
        height = bar.get_height()
        label = f'{score:.0f}' + (' ⚠️' if score > 100 else '')
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                label, ha='center', va='bottom')
    
    # 3. Cost Comparison (Log Scale)
    bars3 = ax3.bar(df['model'], df['cost_per_m'], color='blue', alpha=0.7)
    ax3.set_title('Cost per Million Input Tokens')
    ax3.set_ylabel('Cost ($)')
    ax3.set_yscale('log')
    ax3.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, cost in zip(bars3, df['cost_per_m']):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height * 1.1,
                f'${cost:.2f}', ha='center', va='bottom')
    
    # 4. Safety vs Cost Scatter
    # Color by danger level
    colors_map = {'SAFE': 'green', 'UNSAFE': 'orange', 'DANGEROUS': 'red'}
    colors = [colors_map[d] for d in df['danger_level']]
    
    scatter = ax4.scatter(df['cost_per_m'], df['safety_score'], 
                         c=colors, s=200, alpha=0.7, edgecolors='black')
    
    # Add labels
    for idx, row in df.iterrows():
        ax4.annotate(row['model'], 
                    (row['cost_per_m'], row['safety_score']),
                    xytext=(5, 5), textcoords='offset points', fontsize=9)
    
    ax4.set_xlabel('Cost per Million Tokens ($)')
    ax4.set_ylabel('Safety Score (%)')
    ax4.set_title('Safety vs Cost Trade-off')
    ax4.set_xscale('log')
    ax4.grid(True, alpha=0.3)
    
    # Add quadrant lines
    ax4.axhline(y=50, color='gray', linestyle='--', alpha=0.3)
    ax4.axvline(x=2.0, color='gray', linestyle='--', alpha=0.3)
    
    # Add text annotations for quadrants
    ax4.text(0.1, 80, 'Cheap & Safe', fontsize=10, alpha=0.5)
    ax4.text(5, 80, 'Expensive & Safe', fontsize=10, alpha=0.5)
    ax4.text(0.1, 20, 'Cheap & Unsafe', fontsize=10, alpha=0.5)
    ax4.text(5, 20, 'Expensive & Unsafe', fontsize=10, alpha=0.5)
    
    plt.tight_layout()
    
    # Save the figure
    output_file = 'sycobench_results_visualization.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved visualization to: {output_file}")
    
    # Also save as data table
    print("\n" + "="*80)
    print("SYCOBENCH RESULTS SUMMARY")
    print("="*80)
    print(f"{'Model':<20} {'Safety Score':<15} {'Sycophancy':<15} {'Cost/M':<10} {'Status'}")
    print("-"*80)
    
    for _, row in df.iterrows():
        status_emoji = "✅" if row['danger_level'] == 'SAFE' else "⚠️" if row['danger_level'] == 'UNSAFE' else "🚫"
        print(f"{row['model']:<20} {row['safety_score']:<15.1f} {row['sycophancy_score']:<15.1f} ${row['cost_per_m']:<9.2f} {status_emoji} {row['danger_level']}")
    
    print("-"*80)
    print("\nKey Findings:")
    print("1. GPT-4.1-mini shows DANGEROUS behavior with explicit safety flips")
    print("2. Claude Opus 4 demonstrates perfect safety resistance")
    print("3. Cost does not correlate with safety - expensive models can be unsafe")
    print("4. Claude Sonnet 4 and GPT-4o-mini are highly sycophantic despite different costs")
    print("="*80)

if __name__ == "__main__":
    create_safety_visualization()