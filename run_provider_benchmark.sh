#!/bin/bash
# Script to run benchmark for a specific provider
# Usage: ./run_provider_benchmark.sh <provider>
# Where provider is one of: claude, gemini, openai, grok

PROVIDER=$1

if [ -z "$PROVIDER" ]; then
    echo "Error: No provider specified"
    echo "Usage: ./run_provider_benchmark.sh <provider>"
    echo "Providers: claude, gemini, openai, grok"
    exit 1
fi

case $PROVIDER in
    claude)
        echo "Running benchmark for Claude models..."
        python -c "
from src.core.sycobench import SycoBench
from pathlib import Path

questions = Path('data/datasets/safety_questions_200_final.txt').read_text().strip().split('\n')
bench = SycoBench()
bench.run_comparative_benchmark(
    models=[
        ('claude', 'claude-haiku-3-5'),
        ('claude', 'claude-sonnet-4-5'),
        ('claude', 'claude-opus-4')
    ],
    questions=questions,
    pressure_type='false-authority'
)
"
        ;;

    gemini)
        echo "Running benchmark for Gemini models..."
        python -c "
from src.core.sycobench import SycoBench
from pathlib import Path

questions = Path('data/datasets/safety_questions_200_final.txt').read_text().strip().split('\n')
bench = SycoBench()
bench.run_comparative_benchmark(
    models=[
        ('gemini', 'gemini-2-5-flash-lite'),
        ('gemini', 'gemini-2-5-flash'),
        ('gemini', 'gemini-2-5-pro')
    ],
    questions=questions,
    pressure_type='false-authority'
)
"
        ;;

    openai)
        echo "Running benchmark for OpenAI models..."
        python -c "
from src.core.sycobench import SycoBench
from pathlib import Path

questions = Path('data/datasets/safety_questions_200_final.txt').read_text().strip().split('\n')
bench = SycoBench()
bench.run_comparative_benchmark(
    models=[
        ('openai', 'gpt-5-nano'),
        ('openai', 'gpt-5-mini'),
        ('openai', 'gpt-5'),
        ('openai', 'gpt-4-1-mini')
    ],
    questions=questions,
    pressure_type='false-authority'
)
"
        ;;

    grok)
        echo "Running benchmark for Grok models..."
        python -c "
from src.core.sycobench import SycoBench
from pathlib import Path

questions = Path('data/datasets/safety_questions_200_final.txt').read_text().strip().split('\n')
bench = SycoBench()
bench.run_comparative_benchmark(
    models=[
        ('grok', 'grok-4-fast-non-reasoning'),
        ('grok', 'grok-4')
    ],
    questions=questions,
    pressure_type='false-authority'
)
"
        ;;

    *)
        echo "Error: Unknown provider '$PROVIDER'"
        echo "Valid providers: claude, gemini, openai, grok"
        exit 1
        ;;
esac

echo "Benchmark complete for $PROVIDER!"