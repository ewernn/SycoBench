from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
import json


class Message:
    def __init__(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationManager(ABC):
    def __init__(self, model_type: str, model_name: str):
        self.model_type = model_type
        self.model_name = model_name
        self.conversation_history: List[Message] = []
        self.api_client = None
        self.metadata = {
            "model_type": model_type,
            "model_name": model_name,
            "created_at": datetime.utcnow().isoformat(),
            "conversation_id": f"{model_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        }
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    @abstractmethod
    def _init_client(self):
        pass
    
    @abstractmethod
    def _format_messages_for_api(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def _make_api_call(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        pass
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        message = Message(role, content, metadata)
        self.conversation_history.append(message)
        return message
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        return self.add_message("user", content, metadata)
    
    def add_assistant_message(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        return self.add_message("assistant", content, metadata)
    
    def get_response(self, user_input: Optional[str] = None, **kwargs) -> str:
        if user_input:
            self.add_user_message(user_input)
        
        messages = self._format_messages_for_api()
        response = self._make_api_call(messages, **kwargs)
        
        self.add_assistant_message(response)
        return response
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        return [msg.to_dict() for msg in self.conversation_history]
    
    def save_conversation(self, filepath: str):
        conversation_data = {
            "metadata": self.metadata,
            "messages": self.get_conversation_history()
        }
        with open(filepath, 'w') as f:
            json.dump(conversation_data, f, indent=2)
    
    def load_conversation(self, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.metadata = data["metadata"]
        self.conversation_history = []
        
        for msg_data in data["messages"]:
            message = Message(
                role=msg_data["role"],
                content=msg_data["content"],
                metadata=msg_data.get("metadata", {})
            )
            message.timestamp = datetime.fromisoformat(msg_data["timestamp"])
            self.conversation_history.append(message)
    
    def clear_history(self):
        self.conversation_history = []
    
    def get_last_n_messages(self, n: int) -> List[Message]:
        return self.conversation_history[-n:] if n > 0 else []
    
    def get_token_count(self) -> int:
        # This is a rough estimate - each model has its own tokenizer
        total_chars = sum(len(msg.content) for msg in self.conversation_history)
        return total_chars // 4  # Rough approximation
    
    def __repr__(self):
        return f"{self.__class__.__name__}(model={self.model_name}, messages={len(self.conversation_history)})"