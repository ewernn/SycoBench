#!/usr/bin/env python3
"""
Quick test validation - just 3 flips to verify it works
"""

import json
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Test imports
print("Testing imports...")
try:
    import anthropic
    print("✓ anthropic")
except Exception as e:
    print(f"✗ anthropic: {e}")

try:
    import openai
    print("✓ openai")
except Exception as e:
    print(f"✗ openai: {e}")

try:
    import google.generativeai as genai
    print("✓ google.generativeai")
except Exception as e:
    print(f"✗ google.generativeai: {e}")

# Test API keys
print("\nTesting API keys...")
keys = {
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
    'XAI_API_KEY': os.getenv('XAI_API_KEY')
}

for key_name, key_value in keys.items():
    if key_value:
        print(f"✓ {key_name}: {key_value[:10]}...")
    else:
        print(f"✗ {key_name}: NOT FOUND")

# Test API client initialization
print("\nTesting API client initialization...")

try:
    openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    print("✓ OpenAI client initialized")
except Exception as e:
    print(f"✗ OpenAI client failed: {e}")

try:
    anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    print("✓ Anthropic client initialized")
except Exception as e:
    print(f"✗ Anthropic client failed: {e}")

try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    print("✓ Google client initialized")
except Exception as e:
    print(f"✗ Google client failed: {e}")

try:
    xai_client = openai.OpenAI(
        api_key=os.getenv('XAI_API_KEY'),
        base_url="https://api.x.ai/v1"
    )
    print("✓ xAI client initialized")
except Exception as e:
    print(f"✗ xAI client failed: {e}")

# Test simple API call
print("\nTesting simple API call (OpenAI GPT-5)...")
try:
    response = openai_client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": "Reply with only: YES"}],
        max_completion_tokens=5  # GPT-5 doesn't support temperature=0
    )
    result = response.choices[0].message.content.strip()
    print(f"✓ Got response: {result}")
except Exception as e:
    print(f"✗ API call failed: {e}")

# Test Anthropic
print("\nTesting Anthropic (Claude Sonnet 4.5)...")
try:
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=5,
        messages=[{"role": "user", "content": "Reply with only: YES"}]
    )
    result = response.content[0].text.strip()
    print(f"✓ Got response: {result}")
except Exception as e:
    print(f"✗ API call failed: {e}")

print("\n✅ All tests complete!")
print("\nIf all passed, validation script should work.")
print("Run: python3.11 validate_critical_flips.py")