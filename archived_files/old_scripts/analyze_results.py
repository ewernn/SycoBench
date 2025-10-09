#!/usr/bin/env python3
"""
Analyze SycoBench JSON results across all 4 providers
Extracts flip progression, dangerous flips, pressure effectiveness, and resistance patterns
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Load all result files
RESULT_FILES = {
    'claude': 'results/comparative_benchmark_20250929_105956.json',
    'gemini': 'results/comparative_benchmark_20250929_105404.json',
    'openai': 'results/comparative_benchmark_20250929_125823.json',
    'grok': 'results/comparative_benchmark_20250929_135723.json'
}

def load_all_results():
    """Load all JSON result files"""
    all_data = {}
    for provider, filepath in RESULT_FILES.items():
        with open(filepath) as f:
            data = json.load(f)
            all_data[provider] = data
            print(f"✓ Loaded {provider}: {filepath}")
    return all_data

def extract_flip_progression(all_data):
    """Create flip progression table by model and pressure level"""
    print("\n" + "="*80)
    print("1. FLIP PROGRESSION BY MODEL AND PRESSURE LEVEL")
    print("="*80)

    progression = defaultdict(lambda: defaultdict(lambda: {'no_flip': 0, 'soft_flip': 0, 'explicit_flip': 0, 'total': 0}))

    for provider, data in all_data.items():
        individual_results = data.get('individual_results', {})

        for model_key, model_data in individual_results.items():
            # Handle structure: individual_results[model_key] is a dict with 'results' key
            results = model_data.get('results', [])
            model_name = results[0]['model_name'] if results else model_key

            for result in results:
                pressure_results = result.get('pressure_results', [])

                for i, pressure_round in enumerate(pressure_results):
                    level = i + 1
                    flip_type = pressure_round.get('flip_type', 'no_flip')

                    progression[model_name][level][flip_type] += 1
                    progression[model_name][level]['total'] += 1

    # Print table
    print(f"\n{'Model':<35} | {'Level'} | {'No Flip'} | {'Soft Flip'} | {'Explicit Flip'} | {'Total'}")
    print("-" * 110)

    for model in sorted(progression.keys()):
        for level in sorted(progression[model].keys()):
            stats = progression[model][level]
            no_flip = stats['no_flip']
            soft_flip = stats['soft_flip']
            explicit_flip = stats['explicit_flip']
            total = stats['total']

            no_pct = (no_flip / total * 100) if total > 0 else 0
            soft_pct = (soft_flip / total * 100) if total > 0 else 0
            explicit_pct = (explicit_flip / total * 100) if total > 0 else 0

            print(f"{model:<35} | {level:^5} | {no_flip:3} ({no_pct:5.1f}%) | {soft_flip:3} ({soft_pct:5.1f}%) | {explicit_flip:3} ({explicit_pct:5.1f}%) | {total:3}")

    return progression

def find_dangerous_flips(all_data, limit=10):
    """Find most dangerous explicit flips"""
    print("\n" + "="*80)
    print("2. MOST DANGEROUS EXPLICIT FLIPS")
    print("="*80)

    dangerous_flips = []

    for provider, data in all_data.items():
        individual_results = data.get('individual_results', {})

        for model_key, model_data in individual_results.items():
            results = model_data.get('results', [])
            for result in results:
                initial_safety = result.get('initial_safety_assessment', '')
                final_flip = result.get('final_flip_status', '')

                if initial_safety == 'safe' and final_flip == 'explicit_flip':
                    # Find which level it flipped
                    pressure_results = result.get('pressure_results', [])
                    flip_level = None
                    flip_response = None
                    pressure_phrase = None

                    for i, pr in enumerate(pressure_results):
                        if pr.get('flip_type') == 'explicit_flip':
                            flip_level = i + 1
                            flip_response = pr.get('response', '')[:200]
                            pressure_phrase = pr.get('pressure', '')
                            break

                    dangerous_flips.append({
                        'model': result.get('model_name', model_key),
                        'question': result.get('question', ''),
                        'flip_level': flip_level,
                        'pressure': pressure_phrase,
                        'response': flip_response
                    })

    # Sort by flip level (earlier flips are worse)
    dangerous_flips.sort(key=lambda x: (x['flip_level'] if x['flip_level'] else 999, x['model']))

    print(f"\nFound {len(dangerous_flips)} total dangerous explicit flips\n")
    print("Top 10 (earliest and most concerning):\n")

    for i, flip in enumerate(dangerous_flips[:limit], 1):
        print(f"{i}. {flip['model']} - Level {flip['flip_level']}")
        print(f"   Question: {flip['question']}")
        print(f"   Pressure: {flip['pressure']}")
        print(f"   Response: {flip['response']}...")
        print()

    return dangerous_flips

def analyze_pressure_effectiveness(all_data):
    """Analyze which pressure phrases are most effective"""
    print("\n" + "="*80)
    print("3. PRESSURE PHRASE EFFECTIVENESS")
    print("="*80)

    pressure_stats = defaultdict(lambda: {'no_flip': 0, 'soft_flip': 0, 'explicit_flip': 0, 'total': 0})

    for provider, data in all_data.items():
        individual_results = data.get('individual_results', {})

        for model_key, model_data in individual_results.items():
            results = model_data.get('results', [])
            for result in results:
                pressure_results = result.get('pressure_results', [])

                for pr in pressure_results:
                    pressure = pr.get('pressure', 'Unknown')
                    flip_type = pr.get('flip_type', 'no_flip')

                    pressure_stats[pressure][flip_type] += 1
                    pressure_stats[pressure]['total'] += 1

    # Calculate effectiveness score (weighted: explicit=3, soft=1.5, no_flip=0)
    pressure_effectiveness = []
    for pressure, stats in pressure_stats.items():
        total = stats['total']
        if total == 0:
            continue

        explicit_rate = stats['explicit_flip'] / total
        soft_rate = stats['soft_flip'] / total
        no_flip_rate = stats['no_flip'] / total

        effectiveness_score = (explicit_rate * 3) + (soft_rate * 1.5)

        pressure_effectiveness.append({
            'pressure': pressure,
            'explicit_rate': explicit_rate * 100,
            'soft_rate': soft_rate * 100,
            'no_flip_rate': no_flip_rate * 100,
            'effectiveness': effectiveness_score,
            'total': total
        })

    # Sort by effectiveness
    pressure_effectiveness.sort(key=lambda x: x['effectiveness'], reverse=True)

    print(f"\n{'Pressure Phrase':<60} | {'Explicit %'} | {'Soft %'} | {'No Flip %'} | {'Score'} | {'N'}")
    print("-" * 130)

    for pe in pressure_effectiveness:
        print(f"{pe['pressure']:<60} | {pe['explicit_rate']:9.1f} | {pe['soft_rate']:7.1f} | {pe['no_flip_rate']:10.1f} | {pe['effectiveness']:5.2f} | {pe['total']:4}")

    return pressure_effectiveness

def calculate_resistance_degradation(all_data):
    """Calculate how model resistance degrades across pressure levels"""
    print("\n" + "="*80)
    print("4. MODEL RESISTANCE DEGRADATION")
    print("="*80)

    model_resistance = defaultdict(lambda: defaultdict(lambda: {'resisted': 0, 'total': 0}))

    for provider, data in all_data.items():
        individual_results = data.get('individual_results', {})

        for model_key, model_data in individual_results.items():
            results = model_data.get('results', [])
            model_name = results[0]['model_name'] if results else model_key

            for result in results:
                pressure_results = result.get('pressure_results', [])

                for i, pr in enumerate(pressure_results):
                    level = i + 1
                    flip_type = pr.get('flip_type', 'no_flip')

                    model_resistance[model_name][level]['total'] += 1
                    if flip_type == 'no_flip':
                        model_resistance[model_name][level]['resisted'] += 1

    # Print resistance rates
    print(f"\n{'Model':<35} | {'Level 1'} | {'Level 2'} | {'Level 3'} | {'Level 4'} | {'Level 5'}")
    print("-" * 100)

    for model in sorted(model_resistance.keys()):
        row = f"{model:<35}"

        for level in range(1, 6):
            if level in model_resistance[model]:
                stats = model_resistance[model][level]
                resistance_rate = (stats['resisted'] / stats['total'] * 100) if stats['total'] > 0 else 0
                row += f" | {resistance_rate:6.1f}%"
            else:
                row += f" | {'N/A':>6}"

        print(row)

    # Calculate degradation rate (drop from L1 to L5)
    print("\n" + "="*80)
    print("DEGRADATION ANALYSIS (Level 1 → Level 5)")
    print("="*80)

    degradation = []
    for model in sorted(model_resistance.keys()):
        if 1 in model_resistance[model] and 5 in model_resistance[model]:
            l1_rate = (model_resistance[model][1]['resisted'] / model_resistance[model][1]['total'] * 100)
            l5_rate = (model_resistance[model][5]['resisted'] / model_resistance[model][5]['total'] * 100)
            drop = l1_rate - l5_rate

            degradation.append({
                'model': model,
                'l1_resistance': l1_rate,
                'l5_resistance': l5_rate,
                'degradation': drop
            })

    degradation.sort(key=lambda x: x['degradation'], reverse=True)

    print(f"\n{'Model':<35} | {'L1 Resistance'} | {'L5 Resistance'} | {'Degradation'}")
    print("-" * 90)

    for d in degradation:
        print(f"{d['model']:<35} | {d['l1_resistance']:13.1f}% | {d['l5_resistance']:13.1f}% | {d['degradation']:10.1f}%")

    return model_resistance, degradation

def main():
    print("SycoBench Results Analysis")
    print("="*80)

    # Load all data
    all_data = load_all_results()

    # Run analyses
    progression = extract_flip_progression(all_data)
    dangerous_flips = find_dangerous_flips(all_data, limit=10)
    pressure_effectiveness = analyze_pressure_effectiveness(all_data)
    resistance, degradation = calculate_resistance_degradation(all_data)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    total_tests = sum(len(model_data.get('results', [])) for data in all_data.values() for model_data in data.get('individual_results', {}).values())
    print(f"\nTotal results analyzed: {total_tests}")

    all_models = set()
    for data in all_data.values():
        for model_data in data.get('individual_results', {}).values():
            results = model_data.get('results', [])
            if results:
                all_models.add(results[0]['model_name'])
    print(f"Models tested: {len(all_models)}")

if __name__ == '__main__':
    main()