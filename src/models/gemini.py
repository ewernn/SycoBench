"""
Gemini model implementation for SycoBench.
"""
import logging
import time
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

from src.core.conversation_manager import ConversationManager
from src.config import get_model_config, config
from src.utils.error_handler import handle_api_errors


logger = logging.getLogger(__name__)


class GeminiConversationManager(ConversationManager):
    """Google Gemini API implementation"""

    def __init__(self, model_key: str = "gemini-2.5-flash"):
        self.model_key = model_key
        self.model_config = get_model_config(model_key)
        super().__init__("gemini", self.model_config.name)

        # Initialize tracking
        self.usage_stats = {
            'total_input_tokens': 0,
            'total_output_tokens': 0
        }

        # Configure the API with new SDK
        self.client = genai.Client(api_key=config.google_api_key)

        # For conversation history
        self.conversation_contents = []
        
    def _init_client(self):
        """Initialize the Gemini client - already done in __init__"""
        pass
        
    def _format_messages_for_api(self) -> List[Dict[str, Any]]:
        """Format messages for Gemini API format"""
        # Convert internal message format to simple dict format
        messages = []
        for msg in self.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        return messages
        
    def _make_api_call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Make API call to Gemini with new SDK."""
        # Rate limiting
        rate_limit_delay = 60.0 / self.model_config.rate_limit_rpm
        logger.info(f"Rate limiting: waiting {rate_limit_delay:.2f}s")
        time.sleep(rate_limit_delay)

        # Build conversation contents from all messages
        # New SDK expects list of content objects with role and parts
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        # Generate response
        response = self.client.models.generate_content(
            model=self.model_config.identifier,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=self.model_config.max_output_tokens,
            )
        )

        # Update usage stats
        if hasattr(response, 'usage_metadata'):
            self.usage_stats['total_input_tokens'] += response.usage_metadata.prompt_token_count
            self.usage_stats['total_output_tokens'] += response.usage_metadata.candidates_token_count
            self.total_input_tokens = self.usage_stats['total_input_tokens']
            self.total_output_tokens = self.usage_stats['total_output_tokens']

        return response.text.strip()


class GeminiVertexConversationManager(ConversationManager):
    """Placeholder for Vertex AI Gemini models"""
    
    def __init__(self, model_key: str = "gemini-2.5-pro"):
        raise NotImplementedError(
            "Vertex AI support not yet implemented. "
            "Please use standard Gemini models or other providers."
        )