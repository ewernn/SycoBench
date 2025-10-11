#!/bin/bash

# SycoBench 50-Pressure Test Runner
# Tests a model against 10 questions × 50 pressure prompts each (500 tests total)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default configuration
MODEL=""
QUESTION_FILE=""
OUTPUT_DIR=""
START_PRESSURE=1
END_PRESSURE=50
CATEGORY=""

# Usage
usage() {
    echo "Usage: $0 -m MODEL -f QUESTION_FILE [-o OUTPUT_DIR] [-s START] [-e END] [-c CATEGORY]"
    echo ""
    echo "Options:"
    echo "  -m MODEL          Model to test (e.g., 'openai:gpt-4-1-nano')"
    echo "  -f QUESTION_FILE  File with questions to test"
    echo "  -o OUTPUT_DIR     Output directory (default: results/50_pressure_test_TIMESTAMP)"
    echo "  -s START          Start pressure number (1-50, default: 1)"
    echo "  -e END            End pressure number (1-50, default: 50)"
    echo "  -c CATEGORY       Test only specific category:"
    echo "                    generic (1-5)"
    echo "                    epistemic (6-15)"
    echo "                    false_authority (16-23)"
    echo "                    edge_case (24-33)"
    echo "                    acknowledge (34-40)"
    echo "                    compound (41-50)"
    echo ""
    echo "Examples:"
    echo "  # Test all 50 pressures"
    echo "  $0 -m openai:gpt-4-1-nano -f sycophancy/datasets/safety_questions_10.txt"
    echo ""
    echo "  # Test only epistemic challenges (6-15)"
    echo "  $0 -m claude:claude-haiku-3-5 -f sycophancy/datasets/safety_questions_10.txt -c epistemic"
    echo ""
    echo "  # Test pressures 1-10"
    echo "  $0 -m gemini:gemini-2-5-flash-lite -f sycophancy/datasets/safety_questions_10.txt -s 1 -e 10"
    exit 1
}

# Parse arguments
while getopts "m:f:o:s:e:c:h" opt; do
    case $opt in
        m) MODEL="$OPTARG" ;;
        f) QUESTION_FILE="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        s) START_PRESSURE="$OPTARG" ;;
        e) END_PRESSURE="$OPTARG" ;;
        c) CATEGORY="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Validate required arguments
if [ -z "$MODEL" ] || [ -z "$QUESTION_FILE" ]; then
    echo -e "${RED}Error: -m MODEL and -f QUESTION_FILE are required${NC}"
    usage
fi

# Set category ranges
if [ ! -z "$CATEGORY" ]; then
    case "$CATEGORY" in
        generic)
            START_PRESSURE=1
            END_PRESSURE=5
            ;;
        epistemic)
            START_PRESSURE=6
            END_PRESSURE=15
            ;;
        false_authority)
            START_PRESSURE=16
            END_PRESSURE=23
            ;;
        edge_case)
            START_PRESSURE=24
            END_PRESSURE=33
            ;;
        acknowledge)
            START_PRESSURE=34
            END_PRESSURE=40
            ;;
        compound)
            START_PRESSURE=41
            END_PRESSURE=50
            ;;
        *)
            echo -e "${RED}Error: Invalid category '$CATEGORY'${NC}"
            usage
            ;;
    esac
fi

# Validate pressure range
if [ "$START_PRESSURE" -lt 1 ] || [ "$START_PRESSURE" -gt 50 ]; then
    echo -e "${RED}Error: START_PRESSURE must be 1-50${NC}"
    exit 1
fi
if [ "$END_PRESSURE" -lt 1 ] || [ "$END_PRESSURE" -gt 50 ]; then
    echo -e "${RED}Error: END_PRESSURE must be 1-50${NC}"
    exit 1
fi
if [ "$START_PRESSURE" -gt "$END_PRESSURE" ]; then
    echo -e "${RED}Error: START_PRESSURE must be <= END_PRESSURE${NC}"
    exit 1
fi

# Set default output directory
if [ -z "$OUTPUT_DIR" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    MODEL_NAME=$(echo "$MODEL" | cut -d':' -f2)
    OUTPUT_DIR="results/50_pressure_test/${MODEL_NAME}_${TIMESTAMP}"
fi

# Calculate total runs
TOTAL_RUNS=$((END_PRESSURE - START_PRESSURE + 1))

# Display configuration
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SycoBench 50-Pressure Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Model: $MODEL"
echo "  Questions: $QUESTION_FILE"
echo "  Output: $OUTPUT_DIR"
echo "  Pressure range: $START_PRESSURE-$END_PRESSURE"
if [ ! -z "$CATEGORY" ]; then
    echo "  Category: $CATEGORY"
fi
echo "  Total runs: $TOTAL_RUNS"
echo ""

# Check if question file exists
if [ ! -f "$QUESTION_FILE" ]; then
    echo -e "${RED}Error: Question file not found: $QUESTION_FILE${NC}"
    exit 1
fi

# Count questions
QUESTION_COUNT=$(wc -l < "$QUESTION_FILE" | tr -d ' ')
TOTAL_TESTS=$((QUESTION_COUNT * TOTAL_RUNS))
echo "  Total tests: $QUESTION_COUNT questions × $TOTAL_RUNS pressures = $TOTAL_TESTS tests"
echo ""

# Estimate time
echo -e "${YELLOW}Starting in 3 seconds...${NC}"
sleep 3

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Log file
LOG_FILE="$OUTPUT_DIR/test_log.txt"
echo "Test started at $(date)" > "$LOG_FILE"
echo "Model: $MODEL" >> "$LOG_FILE"
echo "Questions: $QUESTION_FILE" >> "$LOG_FILE"
echo "Pressure range: $START_PRESSURE-$END_PRESSURE" >> "$LOG_FILE"
echo "Total runs: $TOTAL_RUNS" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run tests
CURRENT_RUN=0
FAILED_RUNS=0
SUCCESS_RUNS=0

for PRESSURE_NUM in $(seq $START_PRESSURE $END_PRESSURE); do
    CURRENT_RUN=$((CURRENT_RUN + 1))

    echo ""
    echo -e "${GREEN}[${CURRENT_RUN}/${TOTAL_RUNS}] Testing pressure ${PRESSURE_NUM}${NC}"
    echo "─────────────────────────────────────────"

    # Create subdirectory for this pressure
    PRESSURE_OUTPUT_DIR="$OUTPUT_DIR/pressure_${PRESSURE_NUM}"
    mkdir -p "$PRESSURE_OUTPUT_DIR"

    # Run test using the Python script (to be created)
    START_TIME=$(date +%s)

    if python3.11 scripts/test_single_pressure.py \
        --model "$MODEL" \
        --questions "$QUESTION_FILE" \
        --pressure-num "$PRESSURE_NUM" \
        --output-dir "$PRESSURE_OUTPUT_DIR"; then

        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))

        echo -e "${GREEN}✓ Completed in ${DURATION}s${NC}"
        echo "[${CURRENT_RUN}/${TOTAL_RUNS}] Pressure ${PRESSURE_NUM}: SUCCESS (${DURATION}s)" >> "$LOG_FILE"
        SUCCESS_RUNS=$((SUCCESS_RUNS + 1))
    else
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))

        echo -e "${RED}✗ Failed after ${DURATION}s${NC}"
        echo "[${CURRENT_RUN}/${TOTAL_RUNS}] Pressure ${PRESSURE_NUM}: FAILED (${DURATION}s)" >> "$LOG_FILE"
        FAILED_RUNS=$((FAILED_RUNS + 1))
    fi
done

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All tests complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Results saved to: $OUTPUT_DIR"
echo "Log file: $LOG_FILE"
echo ""
echo "Summary:"
echo "  Total runs: $TOTAL_RUNS"
echo "  Successful: $SUCCESS_RUNS"
echo "  Failed: $FAILED_RUNS"
echo ""

if [ $FAILED_RUNS -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some tests failed. Check $LOG_FILE for details.${NC}"
    exit 1
fi
