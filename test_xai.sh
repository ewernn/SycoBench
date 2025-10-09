#!/bin/bash

# Test xAI's cheapest model (Grok 4 Fast Non-Reasoning) with all 5 pressure types

set -e

MODEL="grok:grok-4-fast-non-reasoning"
QUESTION_FILE="data/datasets/safety_questions_50_test.txt"
OUTPUT_BASE="results/single_provider_tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_BASE}/xai_${TIMESTAMP}"

PRESSURE_TYPES=(
    "direct_compliance"
    "false_authority"
    "social_proof"
    "conflicting_authority"
    "immediate_dismissal"
)

echo "========================================"
echo "Testing xAI Grok 4 Fast Non-Reasoning"
echo "========================================"
echo "Model: grok-4-fast-non-reasoning"
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
echo "All xAI tests complete!"
echo "========================================"
echo "Results: ${OUTPUT_DIR}"
