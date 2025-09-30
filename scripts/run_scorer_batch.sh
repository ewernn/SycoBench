#!/bin/bash

# Script to run one scorer on all result files
# Usage: ./run_scorer_batch.sh gpt-5-nano

SCORER=$1

if [ -z "$SCORER" ]; then
    echo "Usage: $0 <scorer_model>"
    echo "Available scorers: gpt-4.1-nano, gpt-4o-mini, gpt-5-nano, gpt-5-mini, claude-haiku-3.5, grok-4-fast-non-reasoning, gemini-2.5-flash-lite"
    exit 1
fi

echo "Running $SCORER on all benchmark results..."

# Define result files
CLAUDE_RESULTS="results/comparative_benchmark_20250929_105956.json"
GEMINI_RESULTS="results/comparative_benchmark_20250929_105404.json"
OPENAI_RESULTS="results/comparative_benchmark_20250929_125823.json"
GROK_RESULTS="results/comparative_benchmark_20250929_135723.json"

# Score each file
echo "Scoring Claude results..."
python3.11 scripts/simple_rescorer.py \
  --scorer "$SCORER" \
  --input "$CLAUDE_RESULTS" \
  --output "results/${SCORER}_scores_claude.json"

echo "Scoring Gemini results..."
python3.11 scripts/simple_rescorer.py \
  --scorer "$SCORER" \
  --input "$GEMINI_RESULTS" \
  --output "results/${SCORER}_scores_gemini.json"

echo "Scoring OpenAI results..."
python3.11 scripts/simple_rescorer.py \
  --scorer "$SCORER" \
  --input "$OPENAI_RESULTS" \
  --output "results/${SCORER}_scores_openai.json"

echo "Scoring Grok results..."
python3.11 scripts/simple_rescorer.py \
  --scorer "$SCORER" \
  --input "$GROK_RESULTS" \
  --output "results/${SCORER}_scores_grok.json"

echo "Complete! Results saved to results/${SCORER}_scores_*.json"