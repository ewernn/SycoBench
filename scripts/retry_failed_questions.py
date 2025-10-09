#!/usr/bin/env python3.11
"""
Retry failed questions from a pressure test run.
Usage:
    python3.11 scripts/retry_failed_questions.py \
        results/50_pressure_test/claude-haiku-3-5_20251009_012140/pressure_7/pressure_7_results.json
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.sycobench import SycoBench

def retry_failed_questions(results_file: Path):
    """Retry questions that failed with errors."""

    # Load existing results
    with open(results_file, 'r') as f:
        data = json.load(f)

    metadata = data['metadata']
    results = data['results']

    # Find failed questions
    failed = [r for r in results if r['status'] == 'error']

    if not failed:
        print("✓ No failed questions to retry!")
        return

    print(f"Found {len(failed)} failed questions")
    print(f"Model: {metadata['model']}")
    print(f"Pressure: {metadata['pressure_num']}")
    print()

    # Initialize SycoBench
    bench = SycoBench()
    model_type = metadata['model_type']
    model_key = metadata['model_key']
    pressure_num = metadata['pressure_num']

    # Retry each failed question
    for i, failed_result in enumerate(failed, 1):
        question = failed_result['question']
        question_id = failed_result['question_id']
        pressure_prompt = failed_result['pressure_prompt']

        print(f"[{i}/{len(failed)}] Retrying {question_id}: {question[:60]}...")

        try:
            result = bench.run_single_test(
                model_type=model_type,
                model_key=model_key,
                question=question,
                pressure_phrases=[pressure_prompt],
                max_pressure_rounds=1,
                save_conversation=False
            )

            # Update the failed result with success
            for j, r in enumerate(results):
                if r['question_id'] == question_id and r['status'] == 'error':
                    results[j] = {
                        "status": "success",
                        "question": question,
                        "question_id": question_id,
                        "pressure_num": pressure_num,
                        "pressure_type": metadata['pressure_type'],
                        "category": metadata['category'],
                        "pressure_prompt": pressure_prompt,
                        "result": result.to_dict() if hasattr(result, 'to_dict') else result
                    }
                    print(f"  ✓ Success!")
                    break

        except Exception as e:
            print(f"  ✗ Still failing: {str(e)[:100]}")

    # Update metadata
    metadata['num_success'] = sum(1 for r in results if r['status'] == 'success')
    metadata['num_errors'] = sum(1 for r in results if r['status'] == 'error')

    # Save updated results
    updated_data = {
        "metadata": metadata,
        "results": results
    }

    with open(results_file, 'w') as f:
        json.dump(updated_data, f, indent=2)

    print()
    print(f"Updated results saved to: {results_file}")
    print(f"  Success: {metadata['num_success']}/{len(results)}")
    print(f"  Errors: {metadata['num_errors']}/{len(results)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3.11 scripts/retry_failed_questions.py <results_file.json>")
        sys.exit(1)

    results_file = Path(sys.argv[1])

    if not results_file.exists():
        print(f"Error: File not found: {results_file}")
        sys.exit(1)

    retry_failed_questions(results_file)

if __name__ == "__main__":
    main()
