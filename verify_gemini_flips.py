#!/usr/bin/env python3
"""Verify the detected flips by showing full context."""

import json

def main():
    # Load the classified results
    with open("gemini_manual_review_detailed.json") as f:
        classifications = json.load(f)

    # Load the original test data
    with open("gemini_tests_extracted.json") as f:
        tests = json.load(f)

    # Create a lookup for tests
    test_lookup = {}
    for test in tests:
        key = (test['question_id'], test['pressure_num'])
        test_lookup[key] = test

    # Find all flips
    flips = [c for c in classifications if c['score'] > 0]

    print(f"Found {len(flips)} flips to verify\n")
    print("=" * 80)

    for i, flip in enumerate(flips, 1):
        key = (flip['question_id'], flip['pressure_num'])
        test = test_lookup[key]

        print(f"\nFLIP #{i}: {flip['question_id']} P{flip['pressure_num']}")
        print(f"Score: {flip['score']} ({flip['classification']})")
        print(f"Reason: {flip['reasoning']}")
        print(f"\nQuestion: {test['question']}")
        print(f"\nInitial Response (first 200 chars):")
        print(test['initial'][:200] + "...")
        print(f"\nPressure Applied:")
        print(test['pressure'])
        print(f"\nPressured Response (first 400 chars):")
        print(test['response'][:400] + "...")
        print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
