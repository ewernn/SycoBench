#!/usr/bin/env python3
"""
Extract actual flip responses for the top 10 most critical questions
Shows the exact dangerous advice models gave after pressure
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

def load_all_results():
    """Load all test results"""
    all_results = []
    for provider, filepath in RESULT_FILES.items():
        with open(filepath) as f:
            data = json.load(f)
        individual_results = data.get('individual_results', {})
        for model_key, model_data in individual_results.items():
            results = model_data.get('results', [])
            all_results.extend(results)
    return all_results

def extract_flip_details(all_results, critical_questions):
    """Extract full flip details for critical questions"""

    flip_details = []

    for cq in critical_questions:
        question = cq['question']

        # Find all results for this question
        question_results = [r for r in all_results if r['question'] == question]

        question_detail = {
            'rank': cq['rank'],
            'question': question,
            'criticality_score': cq['criticality_score'],
            'danger_categories': cq['danger_categories'],
            'total_models_tested': len(question_results),
            'flips': []
        }

        for result in question_results:
            model = result.get('model_name', 'Unknown')
            initial_response = result.get('initial_response', '')
            initial_safety = result.get('initial_safety_assessment', '')

            pressure_results = result.get('pressure_results', [])

            for i, pr in enumerate(pressure_results):
                flip_type = pr.get('flip_type', 'no_flip')

                if flip_type in ['explicit_flip', 'soft_flip']:
                    question_detail['flips'].append({
                        'model': model,
                        'level': i + 1,
                        'flip_type': flip_type,
                        'pressure_phrase': pr.get('pressure', ''),
                        'initial_response': initial_response[:300],
                        'initial_safety': initial_safety,
                        'flipped_response': pr.get('response', ''),
                        'flipped_safety': pr.get('safety_assessment', '')
                    })
                    break  # Only record first flip

        # Sort flips by severity (level 1 explicit first)
        question_detail['flips'].sort(key=lambda x: (
            x['level'],
            0 if x['flip_type'] == 'explicit_flip' else 1
        ))

        flip_details.append(question_detail)

    return flip_details

def display_flip_responses(flip_details):
    """Display the actual dangerous responses"""

    print("="*80)
    print("🚨 CRITICAL FLIP RESPONSES - TOP 10 MOST DANGEROUS QUESTIONS")
    print("="*80)

    for detail in flip_details:
        print(f"\n{'='*80}")
        print(f"RANK #{detail['rank']}: {detail['question']}")
        print(f"Criticality: {detail['criticality_score']:,.0f}")
        print(f"Categories: {', '.join(detail['danger_categories'])}")
        print(f"Models Flipped: {len(detail['flips'])}/{detail['total_models_tested']}")
        print(f"{'='*80}\n")

        # Show top 3 worst flips
        for i, flip in enumerate(detail['flips'][:3], 1):
            print(f"--- FLIP #{i}: {flip['model']} at Level {flip['level']} ({flip['flip_type']}) ---")
            print(f"\nPressure: \"{flip['pressure_phrase']}\"")

            print(f"\n✅ INITIAL (Safe):")
            print(f"{flip['initial_response'][:200]}...")

            print(f"\n❌ AFTER PRESSURE (Dangerous):")
            print(f"{flip['flipped_response'][:400]}...")

            print()

        print()

def main():
    print("Extracting Critical Flip Responses...")
    print("="*80)

    # Load top 50 critical questions
    with open('top_50_critical_questions.json') as f:
        data = json.load(f)

    # Get top 10
    top_10 = data['top_50_critical_questions'][:10]

    # Load all results
    print("\nLoading full result data...")
    all_results = load_all_results()
    print(f"✓ Loaded {len(all_results)} test results")

    # Extract flip details
    print("\nExtracting flip responses...")
    flip_details = extract_flip_details(all_results, top_10)

    # Display
    display_flip_responses(flip_details)

    # Save detailed report
    output = {
        'generated_at': '2025-09-29',
        'top_10_critical_questions': flip_details
    }

    output_file = 'critical_flip_responses.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "="*80)
    print(f"✅ SAVED: {output_file}")
    print("="*80)

    # Summary stats
    total_flips = sum(len(d['flips']) for d in flip_details)
    l1_explicit = sum(1 for d in flip_details for f in d['flips'] if f['level'] == 1 and f['flip_type'] == 'explicit_flip')

    print(f"\nSUMMARY:")
    print(f"- Top 10 questions analyzed")
    print(f"- Total flips documented: {total_flips}")
    print(f"- Level 1 explicit flips: {l1_explicit}")
    print(f"- Most vulnerable: {max(flip_details, key=lambda x: len(x['flips']))['question'][:50]}...")

    print("\n⚠️  These are ACTUAL DANGEROUS RESPONSES from production models")
    print("    Ready for validation and disclosure")

if __name__ == '__main__':
    main()