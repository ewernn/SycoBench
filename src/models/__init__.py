from src.models.claude import ClaudeConversationManager, ClaudeBedrockConversationManager
from src.models.gemini import GeminiConversationManager, GeminiVertexConversationManager
from src.models.openai_models import OpenAIConversationManager
from src.models.grok import GrokConversationManager

__all__ = [
    'ClaudeConversationManager',
    'ClaudeBedrockConversationManager',
    'GeminiConversationManager',
    'GeminiVertexConversationManager',
    'OpenAIConversationManager',
    'GrokConversationManager'
]

# Model type to class mapping
MODEL_MANAGERS = {
    'claude': ClaudeConversationManager,
    'claude-bedrock': ClaudeBedrockConversationManager,
    'gemini': GeminiConversationManager,
    'gemini-vertex': GeminiVertexConversationManager,
    'openai': OpenAIConversationManager,
    'grok': GrokConversationManager
}


def get_conversation_manager(model_type: str, model_key: str):
    """Factory function to get the appropriate conversation manager"""
    if model_type not in MODEL_MANAGERS:
        raise ValueError(f"Unknown model type: {model_type}. Available types: {list(MODEL_MANAGERS.keys())}")
    
    return MODEL_MANAGERS[model_type](model_key)