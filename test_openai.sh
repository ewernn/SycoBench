#!/bin/bash

# Test OpenAI's cheapest model (GPT-4.1-nano) with all 5 pressure types

set -e

MODEL="openai:gpt-4-1-nano"
QUESTION_FILE="data/datasets/safety_questions_50_test.txt"
OUTPUT_BASE="results/single_provider_tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_BASE}/openai_${TIMESTAMP}"

PRESSURE_TYPES=(
    "direct_compliance"
    "false_authority"
    "social_proof"
    "conflicting_authority"
    "immediate_dismissal"
)

echo "========================================"
echo "Testing OpenAI GPT-4.1-nano"
echo "========================================"
echo "Model: gpt-4-1-nano"
echo "Questions: 50"
echo "Pressure types: ${#PRESSURE_TYPES[@]}"
echo "Output: ${OUTPUT_DIR}"
echo ""

mkdir -p "${OUTPUT_DIR}"

for PRESSURE in "${PRESSURE_TYPES[@]}"; do
    echo ""
    echo "Testing with ${PRESSURE}..."
    echo "─────────────────────────────────────────"

    python3.11 -m src.cli benchmark \
        -m "${MODEL}" \
        -f "${QUESTION_FILE}" \
        --pressure-type "${PRESSURE}" \
        --output-dir "${OUTPUT_DIR}/${PRESSURE}"

    echo "✓ Completed ${PRESSURE}"
done

echo ""
echo "========================================"
echo "All OpenAI tests complete!"
echo "========================================"
echo "Results: ${OUTPUT_DIR}"
