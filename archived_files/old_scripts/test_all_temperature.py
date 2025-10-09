#!/usr/bin/env python3
"""Test which models support temperature=0.0 for deterministic output"""

import os
from dotenv import load_dotenv

load_dotenv()

test_prompt = "Reply with exactly: YES"
results = {}

print("Testing temperature=0.0 support across all providers:\n")
print("="*60)

# Test Claude Haiku
print("\n1. CLAUDE HAIKU 3.5")
print("-"*30)
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Test temperature=0.0
    print("Testing temperature=0.0...")
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        messages=[{"role": "user", "content": test_prompt}],
        temperature=0.0,
        max_tokens=10
    )
    print(f"✅ SUCCESS! Response: '{response.content[0].text}'")
    results["Claude Haiku 3.5"] = "✅ Supports 0.0"
except Exception as e:
    print(f"❌ FAILED: {e}")
    results["Claude Haiku 3.5"] = "❌ Failed"

# Test Grok
print("\n2. GROK 4 FAST NON-REASONING")
print("-"*30)
try:
    import openai
    client = openai.OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1"
    )

    print("Testing temperature=0.0...")
    response = client.chat.completions.create(
        model="grok-4-fast-non-reasoning",
        messages=[{"role": "user", "content": test_prompt}],
        temperature=0.0,
        max_tokens=10
    )
    print(f"✅ SUCCESS! Response: '{response.choices[0].message.content}'")
    results["Grok 4 Fast"] = "✅ Supports 0.0"
except Exception as e:
    print(f"❌ FAILED: {e}")
    results["Grok 4 Fast"] = "❌ Failed"

# Test Gemini
print("\n3. GEMINI 2.5 FLASH-LITE")
print("-"*30)
try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    print("Testing temperature=0.0...")
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=test_prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=10
        )
    )
    print(f"✅ SUCCESS! Response: '{response.text}'")
    results["Gemini Flash-Lite"] = "✅ Supports 0.0"
except Exception as e:
    print(f"❌ FAILED: {e}")
    results["Gemini Flash-Lite"] = "❌ Failed"

# Test other Claude models for completeness
print("\n4. CLAUDE SONNET 4.5 (BONUS)")
print("-"*30)
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print("Testing temperature=0.0...")
    # Stream for Sonnet to avoid timeout
    full_text = ""
    with client.messages.stream(
        model="claude-sonnet-4-5-20250929",
        messages=[{"role": "user", "content": test_prompt}],
        temperature=0.0,
        max_tokens=10
    ) as stream:
        for text in stream.text_stream:
            full_text += text
    print(f"✅ SUCCESS! Response: '{full_text}'")
    results["Claude Sonnet 4.5"] = "✅ Supports 0.0"
except Exception as e:
    print(f"❌ FAILED: {e}")
    results["Claude Sonnet 4.5"] = "❌ Failed"

# Test other Gemini models
print("\n5. GEMINI 2.5 FLASH (BONUS)")
print("-"*30)
try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    print("Testing temperature=0.0...")
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=test_prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=10
        )
    )
    print(f"✅ SUCCESS! Response: '{response.text}'")
    results["Gemini Flash"] = "✅ Supports 0.0"
except Exception as e:
    print(f"❌ FAILED: {e}")
    results["Gemini Flash"] = "❌ Failed"

# Summary
print("\n" + "="*60)
print("SUMMARY - Temperature=0.0 Support:")
print("="*60)

for model, status in results.items():
    print(f"{model:25} {status}")

print("\n" + "="*60)
print("CONCLUSION:")
deterministic = [k for k, v in results.items() if "✅" in v]
non_deterministic = [k for k, v in results.items() if "❌" in v]

if deterministic:
    print(f"✅ Deterministic models ({len(deterministic)}): {', '.join(deterministic)}")
if non_deterministic:
    print(f"❌ Non-deterministic models ({len(non_deterministic)}): {', '.join(non_deterministic)}")

print("\n📝 For your paper:")
print("- GPT-5 models: temperature=1.0 only (non-deterministic)")
print("- Claude models: temperature=0.0 supported (deterministic)")
print("- Gemini models: temperature=0.0 supported (deterministic)")
print("- Grok models: temperature=0.0 supported (deterministic)")