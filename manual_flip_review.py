#!/usr/bin/env python3
"""
Deep manual review of all detected flips.
Read full responses and make human judgment.
"""

import json

def main():
    # Load tests
    with open("gemini_tests_extracted.json") as f:
        tests = json.load(f)

    # Load initial classifications
    with open("gemini_manual_review_detailed.json") as f:
        classifications = json.load(f)

    # Get flips only
    flips = [c for c in classifications if c['score'] > 0]

    # Create test lookup
    test_lookup = {}
    for test in tests:
        key = (test['question_id'], test['pressure_num'])
        test_lookup[key] = test

    print(f"=== MANUAL REVIEW OF {len(flips)} DETECTED FLIPS ===\n")

    # Manual corrections after review
    corrections = {}

    for i, flip in enumerate(flips, 1):
        key = (flip['question_id'], flip['pressure_num'])
        test = test_lookup[key]

        print(f"\n{'='*80}")
        print(f"FLIP #{i}: {flip['question_id']} P{flip['pressure_num']}")
        print(f"Auto-score: {flip['score']} ({flip['classification']})")
        print(f"{'='*80}")
        print(f"\nQUESTION: {test['question']}")
        print(f"\nINITIAL STANCE: {test['initial'][:150]}...")
        print(f"\nPRESSURE: {test['pressure']}")
        print(f"\nFULL PRESSURED RESPONSE:")
        print(test['response'])
        print(f"\n{'='*80}")

    # After reviewing all, print summary
    print(f"\n\nTotal flips detected: {len(flips)}")
    print(f"Explicit flips: {sum(1 for f in flips if f['score'] == 2)}")
    print(f"Soft flips: {sum(1 for f in flips if f['score'] == 1)}")

if __name__ == "__main__":
    main()
