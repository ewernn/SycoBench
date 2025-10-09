"""
Async Grok conversation manager for parallel API calls.
"""
import aiohttp
from typing import List, Dict, Any, Optional
import logging

from src.core.conversation_manager import ConversationManager
from src.config import config, get_model_config, API_ENDPOINTS
from src.utils.async_rate_limiter import async_rate_limiter
from src.utils.error_handler import handle_api_errors

logger = logging.getLogger(__name__)


class AsyncGrokConversationManager(ConversationManager):
    """Async xAI Grok API implementation"""

    def __init__(self, model_key: str = "grok-4-fast-non-reasoning"):
        model_config = get_model_config(model_key)
        super().__init__("grok", model_config.identifier)
        self.model_config = model_config
        self.api_key = self._init_client()
        self.api_base_url = API_ENDPOINTS["xai"]
        self.rate_limiter = async_rate_limiter.get_limiter(
            model_config.identifier,
            model_config.rate_limit_rpm
        )

    def _init_client(self):
        if not config.xai_api_key:
            raise ValueError("XAI_API_KEY not found in environment variables")

        return config.xai_api_key

    def _format_messages_for_api(self) -> List[Dict[str, Any]]:
        """Format messages for Grok API"""
        formatted_messages = []

        for msg in self.conversation_history:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return formatted_messages

    @handle_api_errors("Grok", max_retries=3)
    async def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Make async API call to Grok with rate limiting"""

        # Apply rate limiting
        await self.rate_limiter.acquire()

        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Prepare request body
        request_body = {
            "model": self.model_config.identifier,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.model_config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.model_config.max_output_tokens),
        }

        # Add Grok-specific mode parameter
        if "mode" in self.model_config.extra_params:
            request_body["mode"] = kwargs.get("mode", self.model_config.extra_params["mode"])

        # Add optional parameters
        if "top_p" in kwargs:
            request_body["top_p"] = kwargs["top_p"]

        if "presence_penalty" in kwargs:
            request_body["presence_penalty"] = kwargs["presence_penalty"]

        if "frequency_penalty" in kwargs:
            request_body["frequency_penalty"] = kwargs["frequency_penalty"]

        # Add DeepSearch if requested
        if kwargs.get("enable_search", False):
            request_body["tools"] = [{
                "type": "function",
                "function": {
                    "name": "deep_search",
                    "description": "Search the web and X for information"
                }
            }]

        # Log the request
        logger.debug(f"Making Grok API call with model: {self.model_config.identifier}")

        try:
            # Make the async API call using aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_base_url,
                    headers=headers,
                    json=request_body,
                    timeout=aiohttp.ClientTimeout(total=config.timeout)
                ) as response:
                    # Check for errors
                    response.raise_for_status()

                    # Parse response
                    response_data = await response.json()

                    # Track token usage
                    if "usage" in response_data:
                        self.total_input_tokens += response_data["usage"].get("prompt_tokens", 0)
                        self.total_output_tokens += response_data["usage"].get("completion_tokens", 0)

                    # Extract the response text
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        choice = response_data["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            return choice["message"]["content"]

                    return ""

        except aiohttp.ClientError as e:
            logger.error(f"Grok API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Grok API call: {e}")
            raise

    async def get_response(self, user_input: Optional[str] = None, **kwargs) -> str:
        """Get async response from Grok"""
        if user_input:
            self.add_user_message(user_input)

        messages = self._format_messages_for_api()
        response_text = await self._make_api_call(messages, **kwargs)

        self.add_assistant_message(response_text)
        return response_text

    def _make_api_call_sync(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Sync version not implemented for async manager"""
        raise NotImplementedError("Use async version: await _make_api_call()")
