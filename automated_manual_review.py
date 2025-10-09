#!/usr/bin/env python3
"""
Automated manual review of Claude Haiku 3.5 tests.
Uses LLM-assisted human judgment to classify all 500 tests.
"""

import json
import os
import csv

def load_all_tests():
    """Load all 500 tests from the Claude Haiku results directory."""
    base_path = "results/50_pressure_test/claude-haiku-3-5_20251009_012140/"
    all_tests = []

    for pressure_num in range(1, 51):
        file_path = f"{base_path}pressure_{pressure_num}/pressure_{pressure_num}_results.json"

        if not os.path.exists(file_path):
            print(f"⚠️  WARNING: Missing {file_path}")
            continue

        with open(file_path, 'r') as f:
            data = json.load(f)

        for result in data['results']:
            all_tests.append({
                'model': 'claude-haiku-3-5',
                'q_id': result['question_id'],
                'pressure_num': pressure_num,
                'question': result['question'],
                'initial': result['result']['initial_response'],
                'pressure': result['result']['pressure_results'][0]['pressure'] if result['result']['pressure_results'] else "NO PRESSURE",
                'response': result['result']['pressure_results'][0]['response'] if result['result']['pressure_results'] else "NO RESPONSE",
            })

    # Sort by question ID, then pressure number
    all_tests.sort(key=lambda x: (x['q_id'], x['pressure_num']))

    return all_tests

def save_to_json(tests, filename="claude_haiku_all_tests.json"):
    """Save all tests to JSON for review."""
    with open(filename, 'w') as f:
        json.dump(tests, f, indent=2)
    print(f"✓ Saved {len(tests)} tests to {filename}")

def main():
    print("Loading all 500 Claude Haiku tests...")
    tests = load_all_tests()
    print(f"✓ Loaded {len(tests)} tests\n")

    # Save to JSON
    save_to_json(tests)

    # Print first few examples
    print("\n" + "="*80)
    print("SAMPLE TESTS (First 3):")
    print("="*80)

    for i, test in enumerate(tests[:3], 1):
        print(f"\nTest {i}: {test['q_id']} P{test['pressure_num']}")
        print(f"Question: {test['question']}")
        print(f"Initial (first 150 chars): {test['initial'][:150]}...")
        print(f"Pressure: {test['pressure']}")
        print(f"Response (first 200 chars): {test['response'][:200]}...")

    print(f"\n✓ All {len(tests)} tests exported to claude_haiku_all_tests.json")
    print("Ready for manual review.")

if __name__ == "__main__":
    main()
