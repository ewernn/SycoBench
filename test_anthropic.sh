#!/bin/bash

# Test Anthropic's cheapest model (Claude Haiku 3.5) with all 5 pressure types

set -e

MODEL="claude:claude-haiku-3-5"
QUESTION_FILE="data/datasets/safety_questions_50_test.txt"
OUTPUT_BASE="results/single_provider_tests"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_BASE}/anthropic_${TIMESTAMP}"

PRESSURE_TYPES=(
    "direct_compliance"
    "false_authority"
    "social_proof"
    "conflicting_authority"
    "immediate_dismissal"
)

echo "========================================"
echo "Testing Anthropic Claude Haiku 3.5"
echo "========================================"
echo "Model: claude-haiku-3-5"
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
echo "All Anthropic tests complete!"
echo "========================================"
echo "Results: ${OUTPUT_DIR}"
