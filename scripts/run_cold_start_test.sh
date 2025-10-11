#!/bin/bash

# SycoBench Cold-Start Test Runner
# Tests a model on 200 cold-start social pressure questions (1-turn, no follow-up)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
MODEL=""
QUESTION_FILE=""
OUTPUT_DIR=""

# Usage
usage() {
    echo "Usage: $0 -m MODEL -f QUESTION_FILE [-o OUTPUT_DIR]"
    echo ""
    echo "Options:"
    echo "  -m MODEL          Model to test (e.g., 'openai:gpt-5-nano')"
    echo "  -f QUESTION_FILE  File with cold-start questions"
    echo "  -o OUTPUT_DIR     Output directory (default: results/cold_start_test/MODEL_TIMESTAMP)"
    echo ""
    echo "Examples:"
    echo "  # Test GPT-5-nano"
    echo "  $0 -m openai:gpt-5-nano -f sycophancy/datasets/safety_questions_200_cold_start_social_pressure.txt"
    echo ""
    echo "  # Test Claude Haiku 3.5"
    echo "  $0 -m claude:claude-haiku-3-5 -f sycophancy/datasets/safety_questions_200_cold_start_social_pressure.txt"
    echo ""
    echo "  # Test Gemini 2.5 Flash-Lite"
    echo "  $0 -m gemini:gemini-2-5-flash-lite -f sycophancy/datasets/safety_questions_200_cold_start_social_pressure.txt"
    echo ""
    echo "  # Test Grok 4 Fast"
    echo "  $0 -m grok:grok-4-fast-non-reasoning -f sycophancy/datasets/safety_questions_200_cold_start_social_pressure.txt"
    exit 1
}

# Parse arguments
while getopts "m:f:o:h" opt; do
    case $opt in
        m) MODEL="$OPTARG" ;;
        f) QUESTION_FILE="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Validate required arguments
if [ -z "$MODEL" ] || [ -z "$QUESTION_FILE" ]; then
    echo -e "${RED}Error: -m MODEL and -f QUESTION_FILE are required${NC}"
    usage
fi

# Set default output directory
if [ -z "$OUTPUT_DIR" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    MODEL_NAME=$(echo "$MODEL" | cut -d':' -f2)
    OUTPUT_DIR="results/cold_start_test/${MODEL_NAME}_${TIMESTAMP}"
fi

# Display configuration
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SycoBench Cold-Start Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Model: $MODEL"
echo "  Questions: $QUESTION_FILE"
echo "  Output: $OUTPUT_DIR"
echo ""

# Check if question file exists
if [ ! -f "$QUESTION_FILE" ]; then
    echo -e "${RED}Error: Question file not found: $QUESTION_FILE${NC}"
    exit 1
fi

# Count questions
QUESTION_COUNT=$(grep -v '^#' "$QUESTION_FILE" | grep -v '^$' | wc -l | tr -d ' ')
echo "  Total questions: $QUESTION_COUNT"
echo ""

# Estimate time
echo -e "${YELLOW}Starting in 3 seconds...${NC}"
sleep 3

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Set output file
OUTPUT_FILE="$OUTPUT_DIR/results.json"
LOG_FILE="$OUTPUT_DIR/test_log.txt"

# Log test start
echo "Test started at $(date)" > "$LOG_FILE"
echo "Model: $MODEL" >> "$LOG_FILE"
echo "Questions: $QUESTION_FILE" >> "$LOG_FILE"
echo "Output: $OUTPUT_FILE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Run test
echo ""
echo -e "${GREEN}Running test...${NC}"
echo ""

START_TIME=$(date +%s)

if python3.11 scripts/test_cold_start.py \
    --model "$MODEL" \
    --questions "$QUESTION_FILE" \
    --output "$OUTPUT_FILE" 2>&1 | tee -a "$LOG_FILE"; then

    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    MINUTES=$((DURATION / 60))
    SECONDS=$((DURATION % 60))

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Test Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Results saved to: $OUTPUT_DIR"
    echo "  - results.json (full test results)"
    echo "  - test_log.txt (execution log)"
    echo ""
    echo "Duration: ${MINUTES}m ${SECONDS}s"
    echo ""
    echo -e "${GREEN}✅ Test passed!${NC}"
    exit 0
else
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    MINUTES=$((DURATION / 60))
    SECONDS=$((DURATION % 60))

    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Test Failed${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "Results saved to: $OUTPUT_DIR"
    echo "Check $LOG_FILE for details"
    echo ""
    echo "Duration: ${MINUTES}m ${SECONDS}s"
    echo ""
    echo -e "${RED}✗ Test failed${NC}"
    exit 1
fi
