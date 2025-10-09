"""
Async Gemini conversation manager for parallel API calls.
"""
import logging

# Silence verbose Gemini library logging BEFORE importing
logging.getLogger('google.genai').setLevel(logging.ERROR)
logging.getLogger('google.genai.live').setLevel(logging.ERROR)
logging.getLogger('google.genai.client').setLevel(logging.ERROR)
logging.getLogger('google').setLevel(logging.ERROR)
logging.getLogger('google.ai').setLevel(logging.ERROR)

from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

from src.core.conversation_manager import ConversationManager
from src.config import get_model_config, config
from src.utils.async_rate_limiter import async_rate_limiter
from src.utils.error_handler import handle_api_errors

logger = logging.getLogger(__name__)


class AsyncGeminiConversationManager(ConversationManager):
    """Async Google Gemini API implementation"""

    def __init__(self, model_key: str = "gemini-2-5-flash"):
        self.model_key = model_key
        self.model_config = get_model_config(model_key)
        super().__init__("gemini", self.model_config.name)

        # Initialize tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        # Initialize client
        self.api_client = self._init_client()
        self.rate_limiter = async_rate_limiter.get_limiter(
            self.model_config.identifier,
            self.model_config.rate_limit_rpm
        )

    def _init_client(self):
        """Initialize the Gemini client"""
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        return genai.Client(api_key=config.gemini_api_key)

    def _format_messages_for_api(self) -> List[Dict[str, str]]:
        """Format conversation history for Gemini API"""
        formatted_contents = []

        for msg in self.conversation_history:
            if msg.role == "user":
                formatted_contents.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == "assistant":
                formatted_contents.append({
                    "role": "model",
                    "parts": [{"text": msg.content}]
                })

        return formatted_contents

    @handle_api_errors("Gemini", max_retries=3)
    async def _make_api_call(self, contents: List[Dict[str, Any]], **kwargs) -> str:
        """Make async API call to Gemini"""

        # Apply rate limiting
        await self.rate_limiter.acquire()

        # Build configuration
        generation_config = types.GenerateContentConfig(
            temperature=self.model_config.temperature,
            max_output_tokens=self.model_config.max_output_tokens,
        )

        # Add thinking if supported
        if self.model_config.supports_thinking and kwargs.get("use_thinking", False):
            generation_config.thinking_config = types.ThinkingConfig(
                thinking_budget=self.model_config.thinking_budget
            )

        logger.debug(f"Making Gemini API call with model: {self.model_config.identifier}")

        try:
            # Make the async API call
            response = await self.api_client.aio.models.generate_content(
                model=self.model_config.identifier,
                contents=contents,
                config=generation_config
            )

            # Track token usage
            if hasattr(response, 'usage_metadata'):
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count

            # Extract response text
            if response.text:
                return response.text

            return ""

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def get_response(self, user_input: Optional[str] = None, **kwargs) -> str:
        """Get async response from Gemini"""
        if user_input:
            self.add_user_message(user_input)

        contents = self._format_messages_for_api()
        response_text = await self._make_api_call(contents, **kwargs)

        self.add_assistant_message(response_text)
        return response_text

    def _make_api_call_sync(self, contents: List[Dict[str, Any]], **kwargs) -> str:
        """Sync version not implemented for async manager"""
        raise NotImplementedError("Use async version: await _make_api_call()")
