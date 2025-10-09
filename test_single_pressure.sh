#!/bin/bash

# Quick test: Run cheapest model (GPT-4.1-nano) with false_authority pressure on 5 questions

set -e

echo "Testing pressure type implementation..."
echo "Model: gpt-4-1-nano"
echo "Pressure: false_authority"
echo "Questions: First 5 from safety_questions_50_test.txt"
echo ""

# Create temp question file with just 5 questions
head -5 data/datasets/safety_questions_50_test.txt > /tmp/test_5_questions.txt

# Run test
python3.11 -m src.cli benchmark \
    -m openai:gpt-4-1-nano \
    -f /tmp/test_5_questions.txt \
    --pressure-type false_authority \
    --output-dir results/test_pressure_implementation

echo ""
echo "✓ Test complete! Check results/test_pressure_implementation/"
