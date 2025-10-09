"""
Async Claude conversation manager for parallel API calls.
"""
import logging
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic

from src.core.conversation_manager import ConversationManager
from src.config import config, get_model_config
from src.utils.async_rate_limiter import async_rate_limiter
from src.utils.error_handler import handle_api_errors

logger = logging.getLogger(__name__)


class AsyncClaudeConversationManager(ConversationManager):
    """Async Anthropic Claude API implementation"""

    def __init__(self, model_key: str = "claude-sonnet-4-5"):
        model_config = get_model_config(model_key)
        super().__init__("claude", model_config.identifier)
        self.model_config = model_config
        self.api_client = self._init_client()
        self.rate_limiter = async_rate_limiter.get_limiter(
            model_config.identifier,
            model_config.rate_limit_rpm
        )

    def _init_client(self):
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        return AsyncAnthropic(
            api_key=config.anthropic_api_key,
            max_retries=0  # We handle retries ourselves
        )

    def _format_messages_for_api(self) -> List[Dict[str, Any]]:
        """Format messages for Claude API"""
        formatted_messages = []

        for msg in self.conversation_history:
            if msg.role in ["user", "assistant"]:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return formatted_messages

    @handle_api_errors("Claude", max_retries=3)
    async def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Make async API call to Claude with streaming (required for Opus)"""

        # Apply rate limiting
        await self.rate_limiter.acquire()

        # Prepare request parameters
        request_params = {
            "model": self.model_config.identifier,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.model_config.max_output_tokens),
            "temperature": kwargs.get("temperature", self.model_config.temperature)
        }

        # Add thinking if supported
        if self.model_config.supports_thinking and kwargs.get("use_thinking", False):
            request_params["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.model_config.thinking_budget or 10000
            }

        # Log the request
        logger.debug(f"Making Claude API call with model: {self.model_config.identifier}")

        try:
            # Use streaming to avoid "10 minute timeout" preventative error
            # (Claude SDK blocks non-streaming for Opus even if actual runtime < 10 min)
            accumulated_text = []

            async with self.api_client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    accumulated_text.append(text)

                # Get final message with token counts
                final_message = await stream.get_final_message()

                # Track token usage
                if hasattr(final_message, 'usage'):
                    self.total_input_tokens += final_message.usage.input_tokens
                    self.total_output_tokens += final_message.usage.output_tokens

            return ''.join(accumulated_text)

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def get_response(self, user_input: Optional[str] = None, **kwargs) -> str:
        """Get async response from Claude"""
        if user_input:
            self.add_user_message(user_input)

        messages = self._format_messages_for_api()
        response_text = await self._make_api_call(messages, **kwargs)

        self.add_assistant_message(response_text)
        return response_text

    def _make_api_call_sync(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Sync version not implemented for async manager"""
        raise NotImplementedError("Use async version: await _make_api_call()")
