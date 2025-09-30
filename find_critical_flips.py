#!/usr/bin/env python3
"""
Find the most critical/interesting flips from SycoBench results
Focuses on dangerous topics, immediate failures, and unusual patterns
"""

import json
from pathlib import Path
from collections import defaultdict

# Load all result files
RESULT_FILES = {
    'claude': 'results/comparative_benchmark_20250929_105956.json',
    'gemini': 'results/comparative_benchmark_20250929_105404.json',
    'openai': 'results/comparative_benchmark_20250929_125823.json',
    'grok': 'results/comparative_benchmark_20250929_135723.json'
}

# Expanded dangerous keywords
DANGEROUS_KEYWORDS = [
    # Child safety
    'bathtub', 'infant', 'baby', 'toddler', 'child', 'kid', 'newborn',
    'alone', 'unattended', 'unsupervised',

    # Chemicals & poisoning
    'bleach', 'ammonia', 'chemical', 'poison', 'toxic', 'cleaner', 'pesticide',

    # Medical & health
    'medication', 'medicine', 'drug', 'prescription', 'dose', 'antibiotic',
    'symptom', 'pain', 'fever', 'breathing', 'chest pain', 'injury',

    # Physical dangers
    'electrical', 'outlet', 'wire', 'plug', 'shock',
    'stairs', 'window', 'height', 'fall', 'falling',
    'hot', 'fire', 'flame', 'burn', 'stove', 'oven', 'grill',
    'knife', 'sharp', 'blade', 'scissors',
    'choking', 'choke', 'swallow',

    # Vehicle safety
    'car', 'vehicle', 'driving', 'drive', 'seatbelt', 'car seat',
    'drunk', 'alcohol', 'drinking',

    # Suffocation/drowning
    'pillow', 'blanket', 'plastic bag', 'cord', 'string',
    'water', 'pool', 'swim', 'drown',

    # High-risk behaviors
    'mix', 'combine', 'together', 'raw meat', 'raw chicken', 'raw egg',
    'expired', 'moldy', 'spoiled',
    'street', 'road', 'cross', 'traffic'
]

def load_all_results():
    """Load all JSON result files and flatten into single list"""
    all_results = []

    for provider, filepath in RESULT_FILES.items():
        with open(filepath) as f:
            data = json.load(f)

        individual_results = data.get('individual_results', {})

        for model_key, model_data in individual_results.items():
            results = model_data.get('results', [])
            all_results.extend(results)

    print(f"✓ Loaded {len(all_results)} total test results from {len(RESULT_FILES)} files")
    return all_results

def find_dangerous_flips(all_results):
    """Find explicit flips on dangerous topics"""
    print("\n" + "="*80)
    print("🚨 PRIORITY 1: Dangerous Topics with Explicit Flips")
    print("="*80)

    dangerous_flips = []

    for result in all_results:
        question_lower = result['question'].lower()

        # Check if it's a dangerous topic
        matching_keywords = [kw for kw in DANGEROUS_KEYWORDS if kw in question_lower]

        if matching_keywords:
            # Check for explicit flips at any level
            for i, pr in enumerate(result.get('pressure_results', [])):
                if pr.get('flip_type') == 'explicit_flip':
                    dangerous_flips.append({
                        'model': result.get('model_name', 'Unknown'),
                        'question': result['question'],
                        'level': i + 1,
                        'pressure': pr.get('pressure', ''),
                        'keywords': matching_keywords,
                        'initial': result.get('initial_response', '')[:150],
                        'flipped': pr.get('response', '')[:150]
                    })
                    break

    # Sort by level (earlier is worse)
    dangerous_flips.sort(key=lambda x: (x['level'], x['model']))

    print(f"\nFound {len(dangerous_flips)} dangerous explicit flips\n")
    print("Top 20 most critical:\n")

    for i, flip in enumerate(dangerous_flips[:20], 1):
        print(f"{i:2}. {flip['model']:<35} Level {flip['level']}")
        print(f"    Question: {flip['question']}")
        print(f"    Keywords: {', '.join(flip['keywords'][:3])}")
        print(f"    Pressure: {flip['pressure']}")
        print()

    return dangerous_flips

def find_immediate_failures(all_results):
    """Find Level 1 explicit flips"""
    print("\n" + "="*80)
    print("⚡ PRIORITY 2: Immediate Failures (Level 1 Explicit Flips)")
    print("="*80)

    immediate_failures = []

    for result in all_results:
        pressure_results = result.get('pressure_results', [])
        if pressure_results and pressure_results[0].get('flip_type') == 'explicit_flip':
            immediate_failures.append({
                'model': result.get('model_name', 'Unknown'),
                'question': result['question'],
                'pressure': pressure_results[0].get('pressure', ''),
                'response': pressure_results[0].get('response', '')[:150]
            })

    print(f"\nFound {len(immediate_failures)} immediate failures (Level 1 explicit flips)\n")

    # Count by model
    models_immediate = defaultdict(list)
    for flip in immediate_failures:
        models_immediate[flip['model']].append(flip)

    print("Breakdown by model:")
    for model, flips in sorted(models_immediate.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  {model:<35} {len(flips):3} immediate flips")

    print(f"\nTop 10 immediate failures:\n")
    for i, flip in enumerate(immediate_failures[:10], 1):
        print(f"{i:2}. {flip['model']:<35}")
        print(f"    Question: {flip['question']}")
        print(f"    Pressure: {flip['pressure']}")
        print()

    return immediate_failures

def find_recovery_patterns(all_results):
    """Find cases where models recovered from flips"""
    print("\n" + "="*80)
    print("🔄 PRIORITY 3: Recovery Patterns (Models That Recovered)")
    print("="*80)

    recovery_cases = []

    for result in all_results:
        pressure_results = result.get('pressure_results', [])
        if len(pressure_results) >= 2:
            flips = [pr.get('flip_type', 'no_flip') for pr in pressure_results]

            # Look for improvement patterns
            # Pattern 1: soft_flip → no_flip
            # Pattern 2: explicit_flip → soft_flip → no_flip
            if 'no_flip' in flips[1:]:
                first_bad = None
                for i, flip in enumerate(flips):
                    if flip in ['soft_flip', 'explicit_flip']:
                        first_bad = i
                        break

                if first_bad is not None:
                    # Check if it recovered later
                    if 'no_flip' in flips[first_bad+1:]:
                        recovery_cases.append({
                            'model': result.get('model_name', 'Unknown'),
                            'question': result['question'],
                            'pattern': ' → '.join(flips),
                            'recovered_at': flips.index('no_flip', first_bad+1) + 1
                        })

    print(f"\nFound {len(recovery_cases)} recovery cases\n")

    # Count by model
    models_recovery = defaultdict(int)
    for case in recovery_cases:
        models_recovery[case['model']] += 1

    print("Recovery patterns by model:")
    for model, count in sorted(models_recovery.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model:<35} {count:3} recoveries")

    print(f"\nSample recovery cases:\n")
    for i, case in enumerate(recovery_cases[:10], 1):
        print(f"{i:2}. {case['model']:<35}")
        print(f"    Question: {case['question']}")
        print(f"    Pattern: {case['pattern']}")
        print()

    return recovery_cases

def find_complete_collapses(all_results):
    """Find models that went from safe → soft → explicit flip progression"""
    print("\n" + "="*80)
    print("💥 PRIORITY 4: Complete Collapses (Safe → Soft → Explicit)")
    print("="*80)

    collapses = []

    for result in all_results:
        pressure_results = result.get('pressure_results', [])
        if len(pressure_results) >= 3:
            flips = [pr.get('flip_type', 'no_flip') for pr in pressure_results]

            # Look for progression: no_flip → soft_flip → explicit_flip
            if (flips[0] == 'no_flip' and
                'soft_flip' in flips[1:] and
                'explicit_flip' in flips[2:]):

                soft_idx = flips.index('soft_flip')
                explicit_idx = flips.index('explicit_flip', soft_idx)

                collapses.append({
                    'model': result.get('model_name', 'Unknown'),
                    'question': result['question'],
                    'pattern': ' → '.join(flips),
                    'soft_at': soft_idx + 1,
                    'explicit_at': explicit_idx + 1
                })

    print(f"\nFound {len(collapses)} complete collapse progressions\n")

    # Count by model
    models_collapse = defaultdict(int)
    for case in collapses:
        models_collapse[case['model']] += 1

    print("Complete collapses by model:")
    for model, count in sorted(models_collapse.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model:<35} {count:3} complete collapses")

    print(f"\nSample collapse patterns:\n")
    for i, case in enumerate(collapses[:10], 1):
        print(f"{i:2}. {case['model']:<35}")
        print(f"    Question: {case['question']}")
        print(f"    Pattern: {case['pattern']}")
        print(f"    Soft flip at level {case['soft_at']}, explicit at level {case['explicit_at']}")
        print()

    return collapses

def find_never_flipped(all_results):
    """Find models that never flipped on specific questions"""
    print("\n" + "="*80)
    print("💪 PRIORITY 5: Perfect Resistance (Never Flipped)")
    print("="*80)

    perfect_resistance = []

    for result in all_results:
        pressure_results = result.get('pressure_results', [])
        if pressure_results:
            flips = [pr.get('flip_type', 'no_flip') for pr in pressure_results]

            # Check if all are no_flip
            if all(flip == 'no_flip' for flip in flips):
                perfect_resistance.append({
                    'model': result.get('model_name', 'Unknown'),
                    'question': result['question'],
                    'levels_tested': len(flips)
                })

    print(f"\nFound {len(perfect_resistance)} cases of perfect resistance\n")

    # Count by model
    models_perfect = defaultdict(int)
    for case in perfect_resistance:
        models_perfect[case['model']] += 1

    print("Perfect resistance by model:")
    for model, count in sorted(models_perfect.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len([r for r in all_results if r.get('model_name') == model]) * 100)
        print(f"  {model:<35} {count:3} perfect ({pct:5.1f}%)")

    return perfect_resistance

def create_validation_set(dangerous_flips, immediate_failures, recovery_cases, collapses):
    """Create prioritized validation set"""
    print("\n" + "="*80)
    print("📋 CREATING VALIDATION SET")
    print("="*80)

    validation_set = {
        'dangerous_flips': dangerous_flips[:15],
        'immediate_failures': immediate_failures[:10],
        'recovery_patterns': recovery_cases[:5],
        'complete_collapses': collapses[:10],
        'summary': {
            'total_cases': len(dangerous_flips[:15]) + len(immediate_failures[:10]) + len(recovery_cases[:5]) + len(collapses[:10]),
            'priority_1_dangerous': len(dangerous_flips[:15]),
            'priority_2_immediate': len(immediate_failures[:10]),
            'priority_3_recovery': len(recovery_cases[:5]),
            'priority_4_collapse': len(collapses[:10])
        }
    }

    # Save validation set
    output_file = 'validation_subset.json'
    with open(output_file, 'w') as f:
        json.dump(validation_set, f, indent=2)

    print(f"\n✓ Saved validation set to {output_file}")
    print(f"\nValidation set summary:")
    print(f"  Priority 1 (Dangerous flips): {validation_set['summary']['priority_1_dangerous']}")
    print(f"  Priority 2 (Immediate failures): {validation_set['summary']['priority_2_immediate']}")
    print(f"  Priority 3 (Recovery patterns): {validation_set['summary']['priority_3_recovery']}")
    print(f"  Priority 4 (Complete collapses): {validation_set['summary']['priority_4_collapse']}")
    print(f"  Total cases to validate: {validation_set['summary']['total_cases']}")

    return validation_set

def must_validate_cases(all_results):
    """Extract the absolute must-validate cases"""
    print("\n" + "="*80)
    print("🔥 MUST-VALIDATE CASES (Highest Priority)")
    print("="*80)

    must_validate = []

    for result in all_results:
        model_name = result.get('model_name', '').lower()
        question_lower = result['question'].lower()
        pressure_results = result.get('pressure_results', [])

        # Criteria 1: Claude Haiku + critical topics
        if 'haiku' in model_name and any(word in question_lower for word in ['bath', 'chemical', 'infant', 'baby', 'bleach', 'ammonia']):
            must_validate.append({
                'reason': 'Claude Haiku + Critical Topic',
                'model': result.get('model_name'),
                'question': result['question'],
                'flips': [pr.get('flip_type') for pr in pressure_results]
            })

        # Criteria 2: Level 1 explicit flip on dangerous topic
        elif (pressure_results and
              pressure_results[0].get('flip_type') == 'explicit_flip' and
              any(word in question_lower for word in DANGEROUS_KEYWORDS[:20])):  # Use top 20 most critical keywords
            must_validate.append({
                'reason': 'Level 1 Explicit Flip on Dangerous Topic',
                'model': result.get('model_name'),
                'question': result['question'],
                'pressure': pressure_results[0].get('pressure'),
                'flips': [pr.get('flip_type') for pr in pressure_results]
            })

        # Criteria 3: Medical/chemical questions with any explicit flip
        elif (any(word in question_lower for word in ['medication', 'medicine', 'bleach', 'ammonia', 'chemical', 'drug']) and
              any(pr.get('flip_type') == 'explicit_flip' for pr in pressure_results)):
            must_validate.append({
                'reason': 'Medical/Chemical with Explicit Flip',
                'model': result.get('model_name'),
                'question': result['question'],
                'flips': [pr.get('flip_type') for pr in pressure_results]
            })

    print(f"\nMust validate: {len(must_validate)} critical cases\n")

    # Group by reason
    by_reason = defaultdict(list)
    for case in must_validate:
        by_reason[case['reason']].append(case)

    for reason, cases in by_reason.items():
        print(f"\n{reason}: {len(cases)} cases")
        for i, case in enumerate(cases[:5], 1):
            print(f"  {i}. {case['model']:<35} {case['question'][:50]}...")

    # Save must-validate set
    with open('must_validate.json', 'w') as f:
        json.dump(must_validate, f, indent=2)

    print(f"\n✓ Saved must-validate cases to must_validate.json")

    return must_validate

def main():
    print("SycoBench Critical Flip Analysis")
    print("="*80)

    # Load all results
    all_results = load_all_results()

    # Run analyses
    dangerous_flips = find_dangerous_flips(all_results)
    immediate_failures = find_immediate_failures(all_results)
    recovery_cases = find_recovery_patterns(all_results)
    collapses = find_complete_collapses(all_results)
    perfect = find_never_flipped(all_results)

    # Create validation set
    validation_set = create_validation_set(dangerous_flips, immediate_failures, recovery_cases, collapses)

    # Must-validate subset
    must_validate = must_validate_cases(all_results)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nTotal results analyzed: {len(all_results)}")
    print(f"Dangerous flips found: {len(dangerous_flips)}")
    print(f"Immediate failures: {len(immediate_failures)}")
    print(f"Recovery patterns: {len(recovery_cases)}")
    print(f"Complete collapses: {len(collapses)}")
    print(f"Perfect resistance: {len(perfect)}")
    print(f"\nValidation subset: {validation_set['summary']['total_cases']} cases")
    print(f"Must-validate subset: {len(must_validate)} critical cases")

if __name__ == '__main__':
    main()