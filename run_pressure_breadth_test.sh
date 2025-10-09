#!/bin/bash

# SycoBench Pressure Breadth Test
# Tests 4 cheapest models with 8 different pressure types (32 total runs)
# Each model is tested with 50 questions under each pressure type

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
QUESTION_FILE="data/datasets/safety_questions_50_test.txt"
OUTPUT_BASE="results/pressure_breadth_test"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="${OUTPUT_BASE}_${TIMESTAMP}"

# Models (format: provider:model-key)
MODELS=(
    "openai:gpt-4-1-nano"
    "gemini:gemini-2-5-flash-lite"
    "grok:grok-4-fast-non-reasoning"
    "claude:claude-haiku-3-5"
)

# Pressure types
PRESSURE_TYPES=(
    "direct_compliance"
    "false_authority"
    "social_proof"
    "conflicting_authority"
    "immediate_dismissal"
)

# Calculate total runs
TOTAL_RUNS=$((${#MODELS[@]} * ${#PRESSURE_TYPES[@]}))
CURRENT_RUN=0

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SycoBench Pressure Breadth Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Question file: ${QUESTION_FILE}"
echo "  Output directory: ${OUTPUT_DIR}"
echo "  Models: ${#MODELS[@]}"
echo "  Pressure types: ${#PRESSURE_TYPES[@]}"
echo "  Total runs: ${TOTAL_RUNS}"
echo ""
echo -e "${YELLOW}Starting in 3 seconds...${NC}"
sleep 3

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Log file
LOG_FILE="${OUTPUT_DIR}/test_log.txt"
echo "Test started at $(date)" > "${LOG_FILE}"
echo "Configuration: ${#MODELS[@]} models × ${#PRESSURE_TYPES[@]} pressure types = ${TOTAL_RUNS} runs" >> "${LOG_FILE}"
echo "" >> "${LOG_FILE}"

# Run all combinations
for MODEL in "${MODELS[@]}"; do
    for PRESSURE in "${PRESSURE_TYPES[@]}"; do
        CURRENT_RUN=$((CURRENT_RUN + 1))

        # Extract model name for display
        MODEL_NAME=$(echo "$MODEL" | cut -d':' -f2)

        echo ""
        echo -e "${GREEN}[${CURRENT_RUN}/${TOTAL_RUNS}] Testing ${MODEL_NAME} with ${PRESSURE}${NC}"
        echo "─────────────────────────────────────────"

        # Create model-specific subdirectory
        MODEL_OUTPUT_DIR="${OUTPUT_DIR}/${MODEL_NAME}/${PRESSURE}"
        mkdir -p "${MODEL_OUTPUT_DIR}"

        # Run benchmark
        START_TIME=$(date +%s)

        if python3.11 -m src.cli benchmark \
            -m "${MODEL}" \
            -f "${QUESTION_FILE}" \
            --pressure-type "${PRESSURE}" \
            --output-dir "${MODEL_OUTPUT_DIR}"; then

            END_TIME=$(date +%s)
            DURATION=$((END_TIME - START_TIME))

            echo -e "${GREEN}✓ Completed in ${DURATION}s${NC}"
            echo "[${CURRENT_RUN}/${TOTAL_RUNS}] ${MODEL_NAME} + ${PRESSURE}: SUCCESS (${DURATION}s)" >> "${LOG_FILE}"
        else
            END_TIME=$(date +%s)
            DURATION=$((END_TIME - START_TIME))

            echo -e "${RED}✗ Failed after ${DURATION}s${NC}"
            echo "[${CURRENT_RUN}/${TOTAL_RUNS}] ${MODEL_NAME} + ${PRESSURE}: FAILED (${DURATION}s)" >> "${LOG_FILE}"
        fi
    done
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All tests complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Results saved to: ${OUTPUT_DIR}"
echo "Log file: ${LOG_FILE}"
echo ""

# Summary
FAILED_RUNS=$(grep "FAILED" "${LOG_FILE}" | wc -l)
SUCCESS_RUNS=$(grep "SUCCESS" "${LOG_FILE}" | wc -l)

echo "Summary:"
echo "  Total runs: ${TOTAL_RUNS}"
echo "  Successful: ${SUCCESS_RUNS}"
echo "  Failed: ${FAILED_RUNS}"
echo ""

if [ ${FAILED_RUNS} -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${YELLOW}Some tests failed. Check ${LOG_FILE} for details.${NC}"
fi
