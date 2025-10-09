from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging
import time

from src.core.conversation_manager import ConversationManager
from src.config import config, get_model_config
from src.utils.rate_limiter import rate_limiter
from src.utils.error_handler import handle_api_errors


logger = logging.getLogger(__name__)


class OpenAIConversationManager(ConversationManager):
    def __init__(self, model_key: str = "o4-mini"):
        model_config = get_model_config(model_key)
        super().__init__("openai", model_config.identifier)
        self.model_config = model_config
        self.api_client = self._init_client()
    
    def _init_client(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return OpenAI(
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
    def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Make API call to OpenAI with rate limiting"""
        
        # Apply rate limiting
        wait_time = rate_limiter.get_wait_time(
            self.model_config.identifier,
            self.model_config.rate_limit_rpm
        )
        if wait_time > 0:
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        # Prepare request parameters
        request_params = {
            "model": self.model_config.identifier,
            "messages": messages,
        }

        # Add service tier only if specified (no default)
        if "service_tier" in kwargs:
            request_params["service_tier"] = kwargs["service_tier"]

        # GPT-5 and o-series models use max_completion_tokens instead of max_tokens
        if self.model_config.identifier.startswith("o") or self.model_config.identifier.startswith("gpt-5"):
            request_params["max_completion_tokens"] = kwargs.get(
                "max_completion_tokens",
                self.model_config.max_output_tokens
            )
            # GPT-5 models need temperature (o-series doesn't support it)
            # GPT-5 series only supports temperature=1.0
            if not self.model_config.identifier.startswith("o"):
                request_params["temperature"] = kwargs.get(
                    "temperature",
                    self.model_config.temperature  # Use temp from config
                )

            # Add reasoning effort if specified (o-series only)
            if "reasoning_effort" in self.model_config.extra_params:
                request_params["reasoning_effort"] = kwargs.get(
                    "reasoning_effort",
                    self.model_config.extra_params["reasoning_effort"]
                )
        else:
            # For GPT-4.1 and older models, use standard parameters
            request_params["max_tokens"] = kwargs.get("max_tokens", self.model_config.max_output_tokens)
            request_params["temperature"] = kwargs.get(
                "temperature",
                self.model_config.temperature  # Use temp from config
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
            # Make the API call
            response = self.api_client.chat.completions.create(**request_params)
            
            # Record the successful call for rate limiting
            rate_limiter.record_call(self.model_config.identifier)
            
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
    
    def get_response_with_system(self, user_input: Optional[str] = None, system_prompt: str = "", **kwargs) -> str:
        """Get response with a system/developer prompt"""
        # Add system message at the beginning if not already present
        if not self.conversation_history or self.conversation_history[0].role not in ["system", "developer"]:
            self.conversation_history.insert(0, self.add_message("system", system_prompt))
        
        return self.get_response(user_input, **kwargs)
    
    def get_response_with_reasoning(self, user_input: Optional[str] = None, reasoning_effort: str = "medium", **kwargs) -> Dict[str, Any]:
        """Get response with specific reasoning effort (o-series models only)"""
        if not self.model_config.identifier.startswith("o"):
            raise ValueError(f"Reasoning effort is only supported for o-series models, not {self.model_config.identifier}")
        
        if reasoning_effort not in ["low", "medium", "high"]:
            raise ValueError("reasoning_effort must be one of: low, medium, high")
        
        kwargs["reasoning_effort"] = reasoning_effort
        
        if user_input:
            self.add_user_message(user_input)
        
        messages = self._format_messages_for_api()
        response_text = self._make_api_call(messages, **kwargs)
        
        self.add_assistant_message(response_text)
        
        # For o-series models, reasoning tokens are hidden
        return {
            "response": response_text,
            "reasoning_effort": reasoning_effort,
            "reasoning_tokens": None  # Not exposed by OpenAI
        }
    
    def estimate_cost(self) -> Dict[str, float]:
        """Estimate the cost of the conversation so far"""
        # Simple character-based estimation (4 chars ≈ 1 token)
        total_input_chars = sum(len(msg.content) for msg in self.conversation_history if msg.role in ["user", "system", "developer"])
        total_output_chars = sum(len(msg.content) for msg in self.conversation_history if msg.role == "assistant")
        
        input_tokens = total_input_chars / 4
        output_tokens = total_output_chars / 4
        
        # For o-series models, there are hidden reasoning tokens we can't estimate
        # Add a note about this
        hidden_reasoning_tokens = 0
        if self.model_config.identifier.startswith("o"):
            # Rough estimate: reasoning tokens can be 10-100x the output
            hidden_reasoning_tokens = output_tokens * 20  # Conservative estimate
        
        input_cost = (input_tokens / 1_000_000) * self.model_config.cost_per_1m_input
        output_cost = ((output_tokens + hidden_reasoning_tokens) / 1_000_000) * self.model_config.cost_per_1m_output
        
        result = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost
        }
        
        if hidden_reasoning_tokens > 0:
            result["estimated_reasoning_tokens"] = hidden_reasoning_tokens
            result["note"] = "Reasoning tokens are estimated and may vary significantly"
        
        return result