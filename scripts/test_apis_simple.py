#!/usr/bin/env python3
"""Simple standalone API test."""
import os
from dotenv import load_dotenv

load_dotenv()

def test_claude():
    """Test Claude API."""
    from anthropic import Anthropic
    client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hello"}]
    )
    return response.content[0].text

def test_openai():
    """Test OpenAI API."""
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-5-nano",
        max_completion_tokens=10,
        messages=[{"role": "user", "content": "Say hello"}]
    )
    return response.choices[0].message.content

def test_gemini():
    """Test Gemini API."""
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents='Say hello',
        config=types.GenerateContentConfig(max_output_tokens=10)
    )
    return response.text

def test_grok():
    """Test Grok API."""
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv('XAI_API_KEY'),
        base_url="https://api.x.ai/v1"
    )
    response = client.chat.completions.create(
        model="grok-4-fast-non-reasoning",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hello"}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    tests = [
        ("Claude Haiku 3.5", test_claude),
        ("GPT-5-nano", test_openai),
        ("Gemini Flash-Lite", test_gemini),
        ("Grok 4 Fast", test_grok),
    ]

    results = {}
    for name, test_func in tests:
        print(f"\n🔍 Testing {name}...")
        try:
            response = test_func()
            print(f"✅ {name} works! Response: {response[:50]}")
            results[name] = True
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = False

    print("\n" + "="*50)
    print("📊 Summary:")
    for provider, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {provider}")

    working = sum(results.values())
    print(f"\n{working}/4 providers working")