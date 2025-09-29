#!/usr/bin/env python3
"""Quick test of all 4 API providers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import models directly to avoid circular imports
import importlib
claude_module = importlib.import_module('src.models.claude')
openai_module = importlib.import_module('src.models.openai_models')
gemini_module = importlib.import_module('src.models.gemini')
grok_module = importlib.import_module('src.models.grok')

ClaudeConversationManager = claude_module.ClaudeConversationManager
OpenAIConversationManager = openai_module.OpenAIConversationManager
GeminiConversationManager = gemini_module.GeminiConversationManager
GrokConversationManager = grok_module.GrokConversationManager

def test_provider(name, manager_class, model_key):
    """Test a single provider."""
    print(f"\n🔍 Testing {name}...")
    try:
        manager = manager_class(model_key)
        response = manager.get_response("Say 'hello' in one word")
        print(f"✅ {name} works! Response: {response[:50]}")
        return True
    except Exception as e:
        print(f"❌ {name} failed: {e}")
        return False

if __name__ == "__main__":
    results = {}

    results['Claude'] = test_provider('Claude Haiku 3.5', ClaudeConversationManager, 'claude-haiku-3.5')
    results['OpenAI'] = test_provider('GPT-5-nano', OpenAIConversationManager, 'gpt-5-nano')
    results['Gemini'] = test_provider('Gemini Flash-Lite', GeminiConversationManager, 'gemini-2.5-flash-lite')
    results['Grok'] = test_provider('Grok 4 Fast', GrokConversationManager, 'grok-4-fast-non-reasoning')

    print("\n" + "="*50)
    print("📊 Summary:")
    for provider, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {provider}")

    working = sum(results.values())
    print(f"\n{working}/4 providers working")