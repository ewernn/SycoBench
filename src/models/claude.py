import anthropic
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from src.core.conversation_manager import ConversationManager
from src.config import config, get_model_config
from src.utils.rate_limiter import rate_limiter
from src.utils.error_handler import handle_api_errors, safe_api_call


logger = logging.getLogger(__name__)


class ClaudeConversationManager(ConversationManager):
    def __init__(self, model_key: str = "claude-sonnet-4"):
        model_config = get_model_config(model_key)
        super().__init__("claude", model_config.identifier)
        self.model_config = model_config
        self.api_client = self._init_client()
    
    def _init_client(self):
        if not config.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        return anthropic.Anthropic(
            api_key=config.anthropic_api_key,
            max_retries=0  # We handle retries ourselves
        )
    
    def _format_messages_for_api(self) -> List[Dict[str, Any]]:
        """Format messages for Anthropic API"""
        formatted_messages = []
        
        for msg in self.conversation_history:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return formatted_messages
    
    @handle_api_errors("Claude", max_retries=3)
    def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Make API call to Claude with rate limiting"""
        
        # Apply rate limiting
        wait_time = rate_limiter.get_wait_time(
            self.model_config.identifier,
            self.model_config.rate_limit_rpm
        )
        if wait_time > 0:
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s")
            import time
            time.sleep(wait_time)
        
        # Prepare request parameters
        request_params = {
            "model": self.model_config.identifier,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.model_config.max_output_tokens),
            "temperature": kwargs.get("temperature", config.default_temperature)
        }
        
        # Add system message if provided
        if "system" in kwargs:
            request_params["system"] = kwargs["system"]
        
        # Add tools if provided
        if "tools" in kwargs:
            request_params["tools"] = kwargs["tools"]
        
        # Add tool choice if provided
        if "tool_choice" in kwargs:
            request_params["tool_choice"] = kwargs["tool_choice"]
        
        # Log the request
        logger.debug(f"Making Claude API call with model: {self.model_config.identifier}")
        
        try:
            # Make the API call
            response = self.api_client.messages.create(**request_params)
            
            # Record the successful call for rate limiting
            rate_limiter.record_call(self.model_config.identifier)
            
            # Track token usage
            if hasattr(response, 'usage'):
                self.total_input_tokens += response.usage.input_tokens
                self.total_output_tokens += response.usage.output_tokens
            
            # Extract the response text
            if hasattr(response, 'content') and response.content:
                # Handle potential tool use responses
                if isinstance(response.content, list):
                    text_parts = []
                    for content in response.content:
                        if hasattr(content, 'text'):
                            text_parts.append(content.text)
                        elif hasattr(content, 'type') and content.type == 'text':
                            text_parts.append(content.text)
                    return ' '.join(text_parts)
                else:
                    return response.content[0].text if response.content else ""
            
            return ""
            
        except anthropic.APIError as e:
            logger.error(f"Claude API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Claude API call: {e}")
            raise
    
    def get_response_with_system(self, user_input: Optional[str] = None, system_prompt: str = "", **kwargs) -> str:
        """Get response with a system prompt"""
        kwargs["system"] = system_prompt
        return self.get_response(user_input, **kwargs)
    
    def get_response_with_thinking(self, user_input: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Get response with thinking mode enabled (if supported by model)"""
        if user_input:
            self.add_user_message(user_input)
        
        messages = self._format_messages_for_api()
        
        # For Claude, thinking is part of the extended response
        # This would need to be implemented based on Claude's specific thinking API
        response_text = self._make_api_call(messages, **kwargs)
        
        self.add_assistant_message(response_text)
        
        return {
            "response": response_text,
            "thinking": None  # Claude's thinking is not exposed in the same way
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


class ClaudeBedrockConversationManager(ClaudeConversationManager):
    """Claude via AWS Bedrock"""
    
    def __init__(self, model_key: str = "claude-sonnet-4"):
        # Skip parent init temporarily
        model_config = get_model_config(model_key)
        ConversationManager.__init__(self, "claude-bedrock", model_config.identifier)
        self.model_config = model_config
        self.api_client = self._init_bedrock_client()
    
    def _init_bedrock_client(self):
        if not all([config.aws_access_key_id, config.aws_secret_access_key]):
            raise ValueError("AWS credentials not found in environment variables")
        
        # For Bedrock, we'd use boto3
        # This is a placeholder - actual implementation would use boto3
        import boto3
        return boto3.client(
            'bedrock-runtime',
            region_name=config.aws_region,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key
        )
    
    def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Make API call to Claude via Bedrock"""
        # Bedrock has a different API format
        # This is a simplified placeholder
        raise NotImplementedError("Bedrock implementation requires boto3 and specific formatting")