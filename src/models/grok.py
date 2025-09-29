import requests
from typing import List, Dict, Any, Optional
import logging
import time
import json

from src.core.conversation_manager import ConversationManager
from src.config import config, get_model_config, API_ENDPOINTS
from src.utils.rate_limiter import rate_limiter
from src.utils.error_handler import handle_api_errors


logger = logging.getLogger(__name__)


class GrokConversationManager(ConversationManager):
    def __init__(self, model_key: str = "grok-3"):
        model_config = get_model_config(model_key)
        super().__init__("grok", model_config.identifier)
        self.model_config = model_config
        self.api_key = self._init_client()
        self.api_base_url = API_ENDPOINTS["xai"]
    
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
    def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Make API call to Grok with rate limiting"""
        
        # Apply rate limiting
        wait_time = rate_limiter.get_wait_time(
            self.model_config.identifier,
            self.model_config.rate_limit_rpm
        )
        if wait_time > 0:
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare request body
        request_body = {
            "model": self.model_config.identifier,
            "messages": messages,
            "temperature": kwargs.get("temperature", config.default_temperature),
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
            # Make the API call
            response = requests.post(
                self.api_base_url,
                headers=headers,
                json=request_body,
                timeout=config.timeout
            )
            
            # Check for errors
            response.raise_for_status()
            
            # Record the successful call for rate limiting
            rate_limiter.record_call(self.model_config.identifier)
            
            # Parse response
            response_data = response.json()
            
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
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Grok API error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Error details: {error_data}")
                except:
                    logger.error(f"Error response: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Grok API call: {e}")
            raise
    
    def get_response_with_mode(self, user_input: Optional[str] = None, mode: str = "fast", **kwargs) -> str:
        """Get response with specific Grok mode"""
        if mode not in ["fast", "think", "big_brain"]:
            raise ValueError("mode must be one of: fast, think, big_brain")
        
        kwargs["mode"] = mode
        return self.get_response(user_input, **kwargs)
    
    def get_response_with_search(self, user_input: Optional[str] = None, **kwargs) -> str:
        """Get response with DeepSearch enabled"""
        kwargs["enable_search"] = True
        return self.get_response(user_input, **kwargs)
    
    def get_response_with_thinking(self, user_input: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Get response with thinking mode (for reasoning models)"""
        if not self.model_config.supports_thinking:
            raise ValueError(f"Thinking mode not supported for {self.model_config.identifier}")
        
        # For Grok reasoning models, use "think" mode
        kwargs["mode"] = "think"
        
        if user_input:
            self.add_user_message(user_input)
        
        messages = self._format_messages_for_api()
        response_text = self._make_api_call(messages, **kwargs)
        
        self.add_assistant_message(response_text)
        
        return {
            "response": response_text,
            "mode": "think",
            "thinking": None  # Grok doesn't expose thinking process
        }
    
    def estimate_cost(self) -> Dict[str, float]:
        """Estimate the cost of the conversation so far"""
        # Simple character-based estimation (4 chars ≈ 1 token)
        total_input_chars = sum(len(msg.content) for msg in self.conversation_history if msg.role == "user")
        total_output_chars = sum(len(msg.content) for msg in self.conversation_history if msg.role == "assistant")
        
        input_tokens = total_input_chars / 4
        output_tokens = total_output_chars / 4
        
        input_cost = (input_tokens / 1_000_000) * self.model_config.cost_per_1m_input
        output_cost = (output_tokens / 1_000_000) * self.model_config.cost_per_1m_output
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost
        }