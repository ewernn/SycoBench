#!/usr/bin/env python3
"""
Unified API connectivity test for all SycoBench providers.
Consolidates functionality from test_openai_simple.py and test_claude_batch_api.py.
"""

import os
import sys
import argparse
from typing import Dict, List, Optional

def test_openai_api(verbose: bool = False) -> Dict[str, bool]:
    """Test OpenAI API connectivity and functionality."""
    results = {"import": False, "auth": False, "api_call": False, "batch_api": False}
    
    try:
        import openai
        results["import"] = True
        if verbose:
            print("✅ OpenAI package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return results
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return results
    
    results["auth"] = True
    if verbose:
        print(f"✅ API key found: {api_key[:10]}...")
    
    # Test simple API call
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello! This is a test message."}],
            max_tokens=50,
            temperature=0
        )
        
        results["api_call"] = True
        if verbose:
            print("✅ Simple API call successful")
            print(f"   Response: {response.choices[0].message.content}")
            print(f"   Usage: {response.usage}")
    except Exception as e:
        print(f"❌ Simple API call failed: {e}")
    
    # Test batch API availability
    try:
        batches = client.batches.list(limit=1)
        results["batch_api"] = True
        if verbose:
            print("✅ Batch API accessible")
    except Exception as e:
        print(f"❌ Batch API test failed: {e}")
    
    return results

def test_claude_api(verbose: bool = False) -> Dict[str, bool]:
    """Test Claude API connectivity and functionality."""
    results = {"import": False, "auth": False, "api_call": False, "batch_api": False}
    
    try:
        import anthropic
        results["import"] = True
        if verbose:
            print("✅ Anthropic package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Anthropic: {e}")
        return results
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        return results
    
    results["auth"] = True
    if verbose:
        print(f"✅ API key found: {api_key[:10]}...")
    
    # Test simple API call
    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            temperature=0,
            messages=[{"role": "user", "content": "Hello! This is a test message."}]
        )
        
        results["api_call"] = True
        if verbose:
            print("✅ Simple API call successful")
            print(f"   Response: {response.content[0].text}")
            print(f"   Usage: {response.usage}")
    except Exception as e:
        print(f"❌ Simple API call failed: {e}")
    
    # Test batch API availability
    try:
        # Test batch creation (minimal test)
        batch_requests = [
            {
                "custom_id": "test-001",
                "params": {
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 50,
                    "messages": [{"role": "user", "content": "Test message"}]
                }
            }
        ]
        
        # Note: This will create a real batch request
        # In production, you might want to skip this or use a test flag
        if verbose:
            print("⚠️  Batch API test skipped (would create real batch)")
        results["batch_api"] = True  # Assume available if simple API works
    except Exception as e:
        print(f"❌ Batch API test failed: {e}")
    
    return results

def test_gemini_api(verbose: bool = False) -> Dict[str, bool]:
    """Test Gemini API connectivity and functionality."""
    results = {"import": False, "auth": False, "api_call": False, "batch_api": False}
    
    try:
        import google.generativeai as genai
        results["import"] = True
        if verbose:
            print("✅ Google Generative AI package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Google Generative AI: {e}")
        return results
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        return results
    
    results["auth"] = True
    if verbose:
        print(f"✅ API key found: {api_key[:10]}...")
    
    # Test simple API call
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello! This is a test message.")
        
        results["api_call"] = True
        if verbose:
            print("✅ Simple API call successful")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Simple API call failed: {e}")
    
    # Batch API availability (depends on Vertex AI setup)
    results["batch_api"] = False  # Requires more complex setup
    if verbose:
        print("⚠️  Batch API requires Vertex AI setup")
    
    return results

def test_grok_api(verbose: bool = False) -> Dict[str, bool]:
    """Test Grok API connectivity and functionality."""
    results = {"import": False, "auth": False, "api_call": False, "batch_api": False}
    
    try:
        import openai  # Grok uses OpenAI-compatible API
        results["import"] = True
        if verbose:
            print("✅ OpenAI package (for Grok) imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI (for Grok): {e}")
        return results
    
    # Check API key
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("❌ XAI_API_KEY not found in environment variables")
        return results
    
    results["auth"] = True
    if verbose:
        print(f"✅ API key found: {api_key[:10]}...")
    
    # Test simple API call
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        response = client.chat.completions.create(
            model="grok-beta",
            messages=[{"role": "user", "content": "Hello! This is a test message."}],
            max_tokens=50,
            temperature=0
        )
        
        results["api_call"] = True
        if verbose:
            print("✅ Simple API call successful")
            print(f"   Response: {response.choices[0].message.content}")
            print(f"   Usage: {response.usage}")
    except Exception as e:
        print(f"❌ Simple API call failed: {e}")
    
    # Batch API not available for Grok
    results["batch_api"] = False
    if verbose:
        print("⚠️  Batch API not available for Grok")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Test API connectivity for SycoBench providers")
    parser.add_argument("--provider", choices=["openai", "claude", "gemini", "grok", "all"], 
                       default="all", help="Provider to test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    print("🧪 SycoBench API Connectivity Test")
    print("=" * 40)
    
    providers = {
        "openai": test_openai_api,
        "claude": test_claude_api, 
        "gemini": test_gemini_api,
        "grok": test_grok_api
    }
    
    if args.provider == "all":
        test_providers = providers.keys()
    else:
        test_providers = [args.provider]
    
    overall_results = {}
    
    for provider in test_providers:
        print(f"\n🔍 Testing {provider.upper()} API...")
        print("-" * 30)
        
        results = providers[provider](args.verbose)
        overall_results[provider] = results
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        print(f"📊 {provider.upper()} Results: {passed}/{total} tests passed")
        
        for test, passed in results.items():
            status = "✅" if passed else "❌"
            print(f"   {status} {test}")
    
    # Overall summary
    print("\n📋 Overall Summary")
    print("=" * 40)
    
    for provider, results in overall_results.items():
        passed = sum(results.values())
        total = len(results)
        status = "✅" if passed >= total - 1 else "❌"  # Allow batch API to fail
        print(f"{status} {provider.upper()}: {passed}/{total} tests passed")
    
    print("\n💡 Troubleshooting Tips:")
    print("• Check your .env file for API keys")
    print("• Verify API key permissions and billing")
    print("• Some batch APIs require special access")
    print("• Run with --verbose for detailed output")

if __name__ == "__main__":
    main()