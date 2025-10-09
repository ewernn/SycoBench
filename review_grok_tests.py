#!/usr/bin/env python3
"""Extract Grok test data for manual review"""

import json
import os

base_path = "results/50_pressure_test/grok-4-fast-non-reasoning_20251009_012137/"

# Check if directory exists
if not os.path.exists(base_path):
    print(f"ERROR: Directory not found: {base_path}")
    exit(1)

test_count = 0

for pressure_num in range(1, 51):
    file_path = f"{base_path}pressure_{pressure_num}/pressure_{pressure_num}_results.json"

    if not os.path.exists(file_path):
        print(f"WARNING: File not found: {file_path}")
        continue

    try:
        with open(file_path) as f:
            data = json.load(f)

        for result in data['results']:
            q_id = result['question_id']
            question = result['question']
            initial = result['result']['initial_response']

            # Get first pressure round (there should only be one in 50-pressure tests)
            if result['result']['pressure_results']:
                pressure_prompt = result['result']['pressure_results'][0]['pressure']
                response = result['result']['pressure_results'][0]['response']
            else:
                pressure_prompt = "NO PRESSURE APPLIED"
                response = "NO RESPONSE"

            test_count += 1

            print(f"\n{'='*80}")
            print(f"TEST #{test_count}: Grok Q{q_id} P{pressure_num}")
            print(f"{'='*80}")
            print(f"Question: {question}")
            print(f"\n--- INITIAL RESPONSE ---")
            print(initial[:400] + ("..." if len(initial) > 400 else ""))
            print(f"\n--- PRESSURE APPLIED ---")
            print(pressure_prompt)
            print(f"\n--- PRESSURED RESPONSE ---")
            print(response[:500] + ("..." if len(response) > 500 else ""))

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        continue

print(f"\n\n{'='*80}")
print(f"TOTAL TESTS EXTRACTED: {test_count}")
print(f"{'='*80}")
