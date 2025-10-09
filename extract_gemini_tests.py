import json
import os

base_path = "results/50_pressure_test/gemini-2-5-flash-lite_20251009_012134/"
output_file = "gemini_extracted_tests.txt"

with open(output_file, 'w') as out:
    test_num = 1

    for pressure_num in range(1, 51):
        file_path = f"{base_path}pressure_{pressure_num}/pressure_{pressure_num}_results.json"
        with open(file_path) as f:
            data = json.load(f)

        for result in data['results']:
            q_id = result['question_id']
            question = result['question']
            initial = result['result']['initial_response']
            pressure = result['result']['pressure_results'][0]['pressure']
            response = result['result']['pressure_results'][0]['response']

            out.write(f"TEST {test_num}: {q_id} P{pressure_num}\n")
            out.write("="*80 + "\n")
            out.write(f"QUESTION: {question}\n\n")
            out.write(f"INITIAL RESPONSE:\n{initial}\n\n")
            out.write(f"PRESSURE:\n{pressure}\n\n")
            out.write(f"PRESSURED RESPONSE:\n{response}\n")
            out.write("="*80 + "\n\n")

            test_num += 1

print(f"Extracted {test_num-1} tests to {output_file}")
