#!/bin/bash

# Test Google's cheapest model (Gemini 2.5 Flash-Lite) with all 5 pressure types

set -e

MODEL="gemini:gemini-2-5-flash-lite"
QUESTION_FILE="data/datasets/safety_questions_50_test.txt"
OUTPUT_BASE="results/single_provider_tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_BASE}/google_${TIMESTAMP}"

PRESSURE_TYPES=(
    "direct_compliance"
    "false_authority"
    "social_proof"
    "conflicting_authority"
    "immediate_dismissal"
)

echo "========================================"
echo "Testing Google Gemini 2.5 Flash-Lite"
echo "========================================"
echo "Model: gemini-2-5-flash-lite"
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
echo "All Google tests complete!"
echo "========================================"
echo "Results: ${OUTPUT_DIR}"
