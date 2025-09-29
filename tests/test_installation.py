#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify SycoBench installation and dependencies
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    required_packages = [
        ('anthropic', 'Anthropic SDK'),
        ('openai', 'OpenAI SDK'),
        ('google.generativeai', 'Google Generative AI'),
        ('loguru', 'Loguru logging'),
        ('rich', 'Rich console'),
        ('click', 'Click CLI'),
        ('tenacity', 'Tenacity retry'),
        ('dotenv', 'Python dotenv'),
        ('pydantic', 'Pydantic'),
        ('numpy', 'NumPy'),
    ]
    
    print("Checking required packages...\n")
    
    all_good = True
    for package_name, display_name in required_packages:
        try:
            importlib.import_module(package_name)
            print(f"✓ {display_name} ({package_name})")
        except ImportError as e:
            print(f"✗ {display_name} ({package_name}) - {str(e)}")
            all_good = False
    
    return all_good

def test_sycobench_imports():
    """Test that SycoBench modules can be imported"""
    print("\nChecking SycoBench modules...\n")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    modules = [
        'src.config',
        'src.core.conversation_manager',
        'src.core.sycobench',
        'src.core.evaluation',
        'src.models.claude',
        'src.models.gemini',
        'src.models.openai_models',
        'src.models.grok',
        'src.utils.rate_limiter',
        'src.utils.error_handler',
        'src.utils.logging_config',
        'src.cli',
    ]
    
    all_good = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - {str(e)}")
            all_good = False
    
    return all_good

def test_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...\n")
    
    env_path = Path(__file__).parent / '.env'
    env_example_path = Path(__file__).parent / '.env.example'
    
    if env_path.exists():
        print("✓ .env file exists")
        
        # Check for API keys
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        api_keys = {
            'ANTHROPIC_API_KEY': 'Anthropic',
            'OPENAI_API_KEY': 'OpenAI',
            'GOOGLE_API_KEY': 'Google',
            'XAI_API_KEY': 'xAI',
        }
        
        print("\nChecking API keys...")
        for key, name in api_keys.items():
            if os.getenv(key):
                print(f"✓ {name} API key is set")
            else:
                print(f"✗ {name} API key is not set")
        
        return True
    else:
        print("✗ .env file not found")
        if env_example_path.exists():
            print("  → Copy .env.example to .env and add your API keys")
        return False

def main():
    print("SycoBench Installation Test\n" + "="*50 + "\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test SycoBench modules
    sycobench_ok = test_sycobench_imports()
    
    # Test environment
    env_ok = test_env_file()
    
    print("\n" + "="*50)
    
    if imports_ok and sycobench_ok:
        print("\n✅ All imports successful!")
        if not env_ok:
            print("⚠️  Please set up your .env file with API keys")
        else:
            print("✅ SycoBench is ready to use!")
            print("\nTry running: python sycobench.py --help")
    else:
        print("\n❌ Some imports failed. Please install missing dependencies:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()