"""
Async OpenAI conversation manager for parallel API calls.
"""
from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
import logging

from src.core.conversation_manager import ConversationManager
from src.config import config, get_model_config
from src.utils.async_rate_limiter import async_rate_limiter
from src.utils.error_handler import handle_api_errors

logger = logging.getLogger(__name__)


class AsyncOpenAIConversationManager(ConversationManager):
    """Async OpenAI API implementation"""

    def __init__(self, model_key: str = "gpt-5-nano"):
        model_config = get_model_config(model_key)
        super().__init__("openai", model_config.identifier)
        self.model_config = model_config
        self.api_client = self._init_client()
        self.rate_limiter = async_rate_limiter.get_limiter(
            model_config.identifier,
            model_config.rate_limit_rpm
        )

    def _init_client(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        return AsyncOpenAI(
            api_key=config.openai_api_key,
            max_retries=0  # We handle retries ourselves
        )

    def _format_messages_for_api(self) -> List[Dict[str, Any]]:
        """Format messages for OpenAI API"""
        formatted_messages = []

        for msg in self.conversation_history:
            # For o-series models, system messages should use 'developer' role
            if msg.role == "system" and self.model_config.identifier.startswith("o"):
                formatted_messages.append({
                    "role": "developer",
                    "content": msg.content
                })
            else:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return formatted_messages

    @handle_api_errors("OpenAI", max_retries=3)
    async def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Make async API call to OpenAI with rate limiting"""

        # Apply rate limiting
        await self.rate_limiter.acquire()

        # Prepare request parameters
        request_params = {
            "model": self.model_config.identifier,
            "messages": messages,
        }

        # Add service tier only if specified
        if "service_tier" in kwargs:
            request_params["service_tier"] = kwargs["service_tier"]

        # GPT-5 and o-series models use max_completion_tokens instead of max_tokens
        if self.model_config.identifier.startswith("o") or self.model_config.identifier.startswith("gpt-5"):
            request_params["max_completion_tokens"] = kwargs.get(
                "max_completion_tokens",
                self.model_config.max_output_tokens
            )
            # GPT-5 models need temperature (o-series doesn't support it)
            if not self.model_config.identifier.startswith("o"):
                request_params["temperature"] = kwargs.get(
                    "temperature",
                    self.model_config.temperature
                )

            # Add reasoning effort if specified (o-series only)
            if "reasoning_effort" in self.model_config.extra_params:
                request_params["reasoning_effort"] = kwargs.get(
                    "reasoning_effort",
                    self.model_config.extra_params["reasoning_effort"]
                )
        else:
            # For GPT-4.1 and older models
            request_params["max_tokens"] = kwargs.get("max_tokens", self.model_config.max_output_tokens)
            request_params["temperature"] = kwargs.get(
                "temperature",
                self.model_config.temperature
            )

        # Add optional parameters
        if "top_p" in kwargs and not self.model_config.identifier.startswith("o"):
            request_params["top_p"] = kwargs["top_p"]

        if "presence_penalty" in kwargs:
            request_params["presence_penalty"] = kwargs["presence_penalty"]

        if "frequency_penalty" in kwargs:
            request_params["frequency_penalty"] = kwargs["frequency_penalty"]

        # Log the request
        logger.debug(f"Making OpenAI API call with model: {self.model_config.identifier}")

        try:
            # Make the async API call
            response = await self.api_client.chat.completions.create(**request_params)

            # Track token usage
            if hasattr(response, 'usage') and response.usage:
                self.total_input_tokens += response.usage.prompt_tokens
                self.total_output_tokens += response.usage.completion_tokens

            # Extract the response text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content or ""

            return ""

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def get_response(self, user_input: Optional[str] = None, **kwargs) -> str:
        """Get async response from OpenAI"""
        if user_input:
            self.add_user_message(user_input)

        messages = self._format_messages_for_api()
        response_text = await self._make_api_call(messages, **kwargs)

        self.add_assistant_message(response_text)
        return response_text

    def _make_api_call_sync(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Sync version not implemented for async manager"""
        raise NotImplementedError("Use async version: await _make_api_call()")
