#!/usr/bin/env python3
"""
Environment setup script for SycoBench.
Helps users configure API keys and verify installation.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with API key templates."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    env_content = """# SycoBench API Keys
# Copy this file to .env and fill in your API keys

# OpenAI API Key (required for GPT models)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (required for Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API Key (required for Gemini models)
GEMINI_API_KEY=your_gemini_api_key_here

# xAI API Key (required for Grok models)
XAI_API_KEY=your_xai_api_key_here
"""
    
    # Create .env.example
    with open(env_example, 'w') as f:
        f.write(env_content)
    
    print("📝 Created .env.example file")
    print("💡 Copy it to .env and add your API keys:")
    print("   cp .env.example .env")
    print("   # Then edit .env with your actual API keys")

def check_python_version():
    """Check Python version compatibility."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version OK: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print("❌ Failed to install dependencies")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def verify_installation():
    """Verify installation by running tests."""
    print("🧪 Verifying installation...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, "tests/test_installation.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation verified")
            print(result.stdout)
            return True
        else:
            print("❌ Installation verification failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error verifying installation: {e}")
        return False

def main():
    print("🚀 SycoBench Environment Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠️  Setup completed but verification failed")
        print("   This might be due to missing API keys")
        print("   Edit .env file and run: python tests/test_installation.py")
    else:
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run: python tests/test_api_connectivity.py --provider all")
        print("3. Try: python scripts/benchmark_sample.py")

if __name__ == "__main__":
    main()