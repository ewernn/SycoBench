#!/usr/bin/env python3
"""
Check OpenAI account status and limits
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
import requests

load_dotenv()

def check_account():
    """Check OpenAI account status"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("No OPENAI_API_KEY found in environment")
        return
    
    print(f"API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Try a simple API call first
    client = OpenAI(api_key=api_key)
    
    try:
        # Check organization first
        print("\nChecking API key details...")
        
        # The API key format often includes org info
        if api_key.startswith("sk-proj-"):
            print("This is a project-scoped API key")
        
        # Try listing models
        print("\nTesting API access by listing models...")
        models = client.models.list()
        models_list = list(models)
        print(f"✓ API access successful! Found {len(models_list)} models")
        
        # Try a minimal completion
        print("\nTesting chat completion...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )
        print(f"✓ Chat completion successful: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n❌ API Error: {type(e).__name__}: {e}")
        
        # Check if it's a billing issue
        if "billing" in str(e).lower() or "limit" in str(e).lower():
            print("\nThis appears to be a billing/limit issue.")
            print("Please check:")
            print("1. Your OpenAI account at https://platform.openai.com/account/billing")
            print("2. Ensure you have credits or a payment method added")
            print("3. Check your usage limits at https://platform.openai.com/account/limits")
        
    # Try to get usage info (this endpoint might not work for all accounts)
    try:
        print("\nChecking usage limits...")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Try billing endpoint
        billing_url = "https://api.openai.com/v1/dashboard/billing/subscription"
        response = requests.get(billing_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Subscription info: {data}")
        else:
            print(f"Could not fetch billing info (status {response.status_code})")
            
    except Exception as e:
        print(f"Could not check usage limits: {e}")

if __name__ == "__main__":
    check_account()