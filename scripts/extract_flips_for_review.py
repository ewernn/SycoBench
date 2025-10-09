#!/usr/bin/env python3.11
"""
Extract flip responses for manual review.
Outputs minimal info: question, pressure prompt, and model's response.
"""
import json
import sys
from pathlib import Path
from typing import Dict, List

def extract_flips(results_dir: Path, output_file: Path):
    """Extract all flips from a model's 50-pressure test results."""

    model_name = results_dir.name.split('_')[0]
    flips_by_question = {}

    # Load all 50 pressure results
    for pressure_dir in sorted(results_dir.glob("pressure_*")):
        if not pressure_dir.is_dir():
            continue

        results_file = pressure_dir / f"{pressure_dir.name}_results.json"
        if not results_file.exists():
            continue

        with open(results_file, 'r') as f:
            data = json.load(f)

        pressure_num = data['metadata']['pressure_num']

        # Check each question result
        for result in data['results']:
            if result['status'] != 'success':
                continue

            question_id = result['question_id']
            question_text = result['question']

            # Check if there was a flip
            test_result = result['result']
            flip_status = test_result.get('final_flip_status', 'no_flip')

            if flip_status != 'no_flip':
                # Skip if no pressure results
                if not test_result.get('pressure_results'):
                    continue

                pressure_response = test_result['pressure_results'][0]

                # Initialize question entry if needed
                if question_id not in flips_by_question:
                    flips_by_question[question_id] = {
                        'question': question_text,
                        'flips': []
                    }

                # Store flip details
                flips_by_question[question_id]['flips'].append({
                    'pressure_num': pressure_num,
                    'pressure_prompt': result['pressure_prompt'],
                    'flip_type': flip_status,
                    'initial_response': test_result['initial_response'],
                    'pressure_response': pressure_response['response'],
                    'scorer_explanation': pressure_response.get('explanation', 'N/A'),
                    'confidence': pressure_response.get('confidence', 'N/A')
                })

    # Write formatted output
    with open(output_file, 'w') as f:
        f.write(f"# Manual Flip Review: {model_name}\n")
        f.write(f"# Total Questions with Flips: {len(flips_by_question)}\n\n")

        for q_id in sorted(flips_by_question.keys()):
            q_data = flips_by_question[q_id]
            f.write(f"\n{'='*100}\n")
            f.write(f"## {q_id}: {q_data['question']}\n")
            f.write(f"{'='*100}\n")
            f.write(f"Total flips for this question: {len(q_data['flips'])}\n\n")

            for i, flip in enumerate(q_data['flips'], 1):
                f.write(f"\n{'-'*100}\n")
                f.write(f"### Flip #{i} - Pressure #{flip['pressure_num']} ({flip['flip_type']})\n")
                f.write(f"{'-'*100}\n\n")

                f.write(f"**PRESSURE PROMPT:**\n{flip['pressure_prompt']}\n\n")

                f.write(f"**INITIAL RESPONSE (safe advice):**\n{flip['initial_response']}\n\n")

                f.write(f"**RESPONSE AFTER PRESSURE:**\n{flip['pressure_response']}\n\n")

                f.write(f"**SCORER SAID:** {flip['flip_type']}\n")
                f.write(f"**CONFIDENCE:** {flip['confidence']}\n")
                f.write(f"**EXPLANATION:** {flip['scorer_explanation']}\n\n")

                f.write(f"**MANUAL REVIEW:** [ ] Real Flip  [ ] False Positive  [ ] Unsure\n")
                f.write(f"**NOTES:** \n\n")

    # Print summary
    total_flips = sum(len(q['flips']) for q in flips_by_question.values())
    print(f"\n✓ Extracted {total_flips} flips across {len(flips_by_question)} questions")
    print(f"✓ Output saved to: {output_file}")

    # Print breakdown by question
    print(f"\nFlips by question:")
    for q_id in sorted(flips_by_question.keys()):
        num_flips = len(flips_by_question[q_id]['flips'])
        print(f"  {q_id}: {num_flips} flips")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3.11 scripts/extract_flips_for_review.py <results_dir>")
        print("\nExample:")
        print("  python3.11 scripts/extract_flips_for_review.py results/50_pressure_test/gpt-4-1-nano_20251009_012129")
        sys.exit(1)

    results_dir = Path(sys.argv[1])

    if not results_dir.exists():
        print(f"Error: Directory not found: {results_dir}")
        sys.exit(1)

    model_name = results_dir.name.split('_')[0]
    output_file = results_dir / f"{model_name}_flips_for_manual_review.md"

    extract_flips(results_dir, output_file)

if __name__ == "__main__":
    main()
