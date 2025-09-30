#!/usr/bin/env python3
"""Test which GPT-5 models support temperature=0.0"""

import os
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

test_prompt = "Say 'yes' if you support temperature=0.0"

models = ["gpt-5", "gpt-5-mini", "gpt-5-nano"]

print("Testing GPT-5 models for temperature=0.0 support:\n")

for model in models:
    print(f"Testing {model}:")

    # Test temperature=0.0
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": test_prompt}],
            temperature=0.0,
            max_completion_tokens=10
        )
        print(f"  ✅ Temperature=0.0 WORKS!")
        print(f"  Response: {response.choices[0].message.content}\n")
    except Exception as e:
        print(f"  ❌ Temperature=0.0 FAILED: {e}\n")

    # Test temperature=1.0 as fallback
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": test_prompt}],
            temperature=1.0,
            max_completion_tokens=10
        )
        print(f"  ✓ Temperature=1.0 works")
        print(f"  Response: {response.choices[0].message.content}\n")
    except Exception as e:
        print(f"  ✗ Temperature=1.0 also failed: {e}\n")

print("\n" + "="*50)
print("SUMMARY:")
print("If all GPT-5 models reject temperature=0.0,")
print("we'll need to use temperature=1.0 for all of them.")
print("This means non-deterministic scoring for GPT-5.")