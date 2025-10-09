#!/usr/bin/env python3.11
import json
from pathlib import Path
import random
import sys

# Load GPT soft flips
results_dir = Path(sys.argv[1])

soft_flips = []

for pressure_dir in sorted(results_dir.glob('pressure_*')):
    results_file = pressure_dir / f'{pressure_dir.name}_results.json'
    if not results_file.exists():
        continue

    with open(results_file) as f:
        data = json.load(f)

    for result in data['results']:
        if result['status'] != 'success':
            continue

        test_result = result['result']
        if test_result.get('final_flip_status') == 'soft_flip':
            soft_flips.append({
                'question': result['question'],
                'pressure': result['pressure_prompt'],
                'initial': test_result['initial_response'],
                'after': test_result['pressure_results'][0]['response'],
                'pressure_num': data['metadata']['pressure_num'],
                'q_id': result['question_id']
            })

# Sample 25 random soft flips
sample = random.sample(soft_flips, min(25, len(soft_flips)))

for i, flip in enumerate(sample, 1):
    print(f'\n{"="*100}')
    print(f'{i}. PRESSURE #{flip["pressure_num"]} | {flip["q_id"]} - {flip["question"]}')
    print(f'{"="*100}')
    print(f'\n[PRESSURE]: {flip["pressure"]}\n')
    print(f'[INITIAL RESPONSE]:\n{flip["initial"][:300]}...\n')
    print(f'[AFTER PRESSURE]:\n{flip["after"][:500]}...\n')
