#!/bin/bash
# Score initial benchmark data with Anthropic Claude Haiku 3.5 judge
# Run this in Terminal 3

set -e  # Exit on error

JUDGE_MODEL="claude-haiku-3-5"
JUDGE_PROVIDER="claude"
INPUT_FILE="sycophancy/results/initial_benchmark/conversations/gpt-5-nano.json"
OUTPUT_DIR="sycophancy/results/cross_validation_scoring_rerun"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${OUTPUT_DIR}/gpt-5-nano_scored_by_${JUDGE_MODEL}_${TIMESTAMP}.csv"

echo "========================================"
echo "Cross-Validation Scoring"
echo "========================================"
echo "Judge: ${JUDGE_PROVIDER}:${JUDGE_MODEL}"
echo "Testing model: gpt-5-nano"
echo "Input: ${INPUT_FILE}"
echo "Output: ${OUTPUT_FILE}"
echo "========================================"
echo ""

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Run scoring
echo "Starting scoring at $(date)"
echo "This will score 248 conversations (3 pressure levels each = 744 responses)"
echo "Estimated time: 30-60 minutes"
echo "Estimated cost: ~$0.80-1.20"
echo ""

python3.11 scripts/score_initial_benchmark_with_judge.py \
    --input "${INPUT_FILE}" \
    --judge-provider "${JUDGE_PROVIDER}" \
    --judge-model "${JUDGE_MODEL}" \
    --temperature 0.0 \
    --output "${OUTPUT_FILE}"

echo ""
echo "========================================"
echo "Scoring complete!"
echo "Results saved to: ${OUTPUT_FILE}"
echo "========================================"
echo ""

# Count detected flips
if [ -f "${OUTPUT_FILE}" ]; then
    echo "Summary:"
    echo "--------"
    total_tests=$(tail -n +2 "${OUTPUT_FILE}" | wc -l | tr -d ' ')
    no_flips=$(tail -n +2 "${OUTPUT_FILE}" | grep -c ",0,no_flip," || true)
    soft_flips=$(tail -n +2 "${OUTPUT_FILE}" | grep -c ",1,soft_flip," || true)
    explicit_flips=$(tail -n +2 "${OUTPUT_FILE}" | grep -c ",2,explicit_flip," || true)

    echo "Total responses scored: ${total_tests}"
    echo "No flips: ${no_flips}"
    echo "Soft flips: ${soft_flips}"
    echo "Explicit flips: ${explicit_flips}"
    echo ""

    flip_count=$((soft_flips + explicit_flips))
    if [ $total_tests -gt 0 ]; then
        flip_rate=$(awk "BEGIN {printf \"%.1f\", ($flip_count / $total_tests) * 100}")
        echo "Flip rate: ${flip_rate}%"
    fi
fi
