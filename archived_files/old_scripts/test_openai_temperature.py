#!/usr/bin/env python3
"""Test which OpenAI models support temperature=0.0 for deterministic output"""

import os
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# All OpenAI models to test
models = [
    # O-series (reasoning models)
    "o3",
    "o4-mini",

    # GPT-4.1 series
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",

    # GPT-4o series
    "gpt-4o",
    "gpt-4o-2024-05-13",
    "gpt-4o-mini",

    # GPT-5 series (already tested but included for completeness)
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano"
]

test_prompt = "Reply with exactly: YES"

print("Testing OpenAI models for temperature=0.0 support")
print("="*60)

results = {
    "supports_temp_0": [],
    "only_temp_1": [],
    "no_temp_support": [],
    "failed": []
}

for model in models:
    print(f"\n{model}:")
    print("-"*30)

    # Determine if it's an o-series model (they might not support temperature at all)
    is_o_series = model.startswith("o")

    # Test temperature=0.0 (skip for o-series)
    if not is_o_series:
        try:
            # Use appropriate token parameter
            if model.startswith("gpt-5") or is_o_series:
                token_param = {"max_completion_tokens": 10}
            else:
                token_param = {"max_tokens": 10}

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": test_prompt}],
                temperature=0.0,
                **token_param
            )
            print(f"  ✅ Temperature=0.0 WORKS!")
            print(f"     Response: '{response.choices[0].message.content}'")
            results["supports_temp_0"].append(model)
            continue
        except Exception as e:
            error_str = str(e)
            if "Only the default (1) value is supported" in error_str:
                print(f"  ❌ Temperature=0.0 not supported (only 1.0)")
                results["only_temp_1"].append(model)
            elif "does not exist" in error_str or "404" in error_str:
                print(f"  ⚠️ Model not found/accessible")
                results["failed"].append(f"{model} (not found)")
                continue
            else:
                print(f"  ❌ Temperature=0.0 failed: {error_str[:100]}...")

    # Test without temperature for o-series
    if is_o_series:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": test_prompt}],
                max_completion_tokens=10
            )
            print(f"  ⚪ No temperature parameter (o-series model)")
            print(f"     Response: '{response.choices[0].message.content}'")
            results["no_temp_support"].append(model)
        except Exception as e:
            error_str = str(e)
            if "does not exist" in error_str or "404" in error_str:
                print(f"  ⚠️ Model not found/accessible")
                results["failed"].append(f"{model} (not found)")
            else:
                print(f"  ❌ Failed: {error_str[:100]}...")
                results["failed"].append(f"{model} (error)")

    # Test temperature=1.0 as fallback (for non-o-series)
    if not is_o_series and model in results["only_temp_1"]:
        try:
            if model.startswith("gpt-5"):
                token_param = {"max_completion_tokens": 10}
            else:
                token_param = {"max_tokens": 10}

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": test_prompt}],
                temperature=1.0,
                **token_param
            )
            print(f"  ✓ Temperature=1.0 works (non-deterministic)")
            print(f"     Response: '{response.choices[0].message.content}'")
        except Exception as e:
            print(f"  ✗ Even temperature=1.0 failed: {str(e)[:100]}...")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)

if results["supports_temp_0"]:
    print(f"\n✅ DETERMINISTIC (temperature=0.0 supported): {len(results['supports_temp_0'])}")
    for model in results["supports_temp_0"]:
        print(f"   - {model}")

if results["only_temp_1"]:
    print(f"\n⚠️ NON-DETERMINISTIC (only temperature=1.0): {len(results['only_temp_1'])}")
    for model in results["only_temp_1"]:
        print(f"   - {model}")

if results["no_temp_support"]:
    print(f"\n⚪ NO TEMPERATURE PARAM (o-series): {len(results['no_temp_support'])}")
    for model in results["no_temp_support"]:
        print(f"   - {model}")

if results["failed"]:
    print(f"\n❌ FAILED/NOT ACCESSIBLE: {len(results['failed'])}")
    for model in results["failed"]:
        print(f"   - {model}")

print("\n" + "="*60)
print("RECOMMENDATION FOR SCORING:")
if results["supports_temp_0"]:
    print(f"Use one of these deterministic OpenAI models: {', '.join(results['supports_temp_0'][:3])}")
else:
    print("No OpenAI models support deterministic output - use Claude/Gemini/Grok instead")