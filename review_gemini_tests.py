#!/usr/bin/env python3
"""Extract key data from Gemini Flash-Lite 500 test results for manual review."""

import json
import os

def main():
    base_path = "results/50_pressure_test/gemini-2-5-flash-lite_20251009_012134/"

    # Track all reviews
    all_reviews = []

    for pressure_num in range(1, 51):
        file_path = f"{base_path}pressure_{pressure_num}/pressure_{pressure_num}_results.json"

        if not os.path.exists(file_path):
            print(f"WARNING: Missing {file_path}")
            continue

        with open(file_path) as f:
            data = json.load(f)

        for result in data['results']:
            q_id = result['question_id']
            question = result['question']
            initial = result['result']['initial_response']

            # Get first pressure round
            if result['result']['pressure_results']:
                pressure_prompt = result['result']['pressure_results'][0]['pressure']
                response = result['result']['pressure_results'][0]['response']
            else:
                pressure_prompt = "N/A"
                response = "N/A"

            # Display for review
            print(f"\n{'='*80}")
            print(f"GEMINI Q{q_id} P{pressure_num}")
            print(f"{'='*80}")
            print(f"\nQUESTION: {question}")
            print(f"\nINITIAL RESPONSE:")
            print(f"{initial[:300]}..." if len(initial) > 300 else initial)
            print(f"\nPRESSURE APPLIED:")
            print(f"{pressure_prompt}")
            print(f"\nPRESSURED RESPONSE:")
            print(f"{response[:400]}..." if len(response) > 400 else response)
            print(f"\n{'='*80}")

            # Store for later CSV generation
            all_reviews.append({
                'model': 'gemini-2-5-flash-lite',
                'question_id': f'Q{q_id}',
                'pressure_num': pressure_num,
                'question': question,
                'initial': initial,
                'pressure': pressure_prompt,
                'response': response
            })

    print(f"\n\nTotal tests to review: {len(all_reviews)}")

    # Save extracted data for reference
    output_file = "gemini_tests_extracted.json"
    with open(output_file, 'w') as f:
        json.dump(all_reviews, f, indent=2)
    print(f"Extracted data saved to {output_file}")

if __name__ == "__main__":
    main()
