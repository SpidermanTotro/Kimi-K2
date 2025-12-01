"""
NEXUS AI - Input Validators
Validation utilities for user inputs and data
"""

import re
from typing import Optional, List, Any
from pathlib import Path

class InputValidator:
    """Validates various types of user inputs"""
    
    @staticmethod
    def validate_api_key(key: str, provider: str = "openai") -> tuple[bool, Optional[str]]:
        """Validate API key format"""
        if not key or not key.strip():
            return False, f"{provider} API key is empty"
        
        if provider == "openai":
            if not key.startswith("sk-"):
                return False, "OpenAI API key should start with 'sk-'"
            if len(key) < 20:
                return False, "OpenAI API key is too short"
        
        elif provider == "anthropic":
            if not key.startswith("sk-ant-"):
                return False, "Anthropic API key should start with 'sk-ant-'"
        
        return True, None
    
    @staticmethod
    def validate_model_name(model: str, available_models: List[str]) -> tuple[bool, Optional[str]]:
        """Validate model name"""
        if not model:
            return False, "Model name is empty"
        
        if model not in available_models:
            return False, f"Model '{model}' not available. Choose from: {', '.join(available_models)}"
        
        return True, None
    
    @staticmethod
    def validate_temperature(temp: float) -> tuple[bool, Optional[str]]:
        """Validate temperature parameter"""
        if not isinstance(temp, (int, float)):
            return False, "Temperature must be a number"
        
        if temp < 0 or temp > 2:
            return False, "Temperature must be between 0 and 2"
        
        return True, None
    
    @staticmethod
    def validate_max_tokens(tokens: int) -> tuple[bool, Optional[str]]:
        """Validate max tokens parameter"""
        if not isinstance(tokens, int):
            return False, "Max tokens must be an integer"
        
        if tokens < 1:
            return False, "Max tokens must be positive"
        
        if tokens > 128000:
            return False, "Max tokens exceeds maximum (128000)"
        
        return True, None
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = False) -> tuple[bool, Optional[str]]:
        """Validate file path"""
        if not path:
            return False, "File path is empty"
        
        try:
            file_path = Path(path)
            
            if must_exist and not file_path.exists():
                return False, f"File does not exist: {path}"
            
            return True, None
        except Exception as e:
            return False, f"Invalid file path: {str(e)}"
    
    @staticmethod
    def validate_file_extension(path: str, allowed_extensions: List[str]) -> tuple[bool, Optional[str]]:
        """Validate file extension"""
        file_path = Path(path)
        ext = file_path.suffix.lower()
        
        if ext not in allowed_extensions:
            return False, f"File extension '{ext}' not allowed. Allowed: {', '.join(allowed_extensions)}"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> tuple[bool, Optional[str]]:
        """Validate URL format"""
        if not url:
            return False, "URL is empty"
        
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, Optional[str]]:
        """Validate email format"""
        if not email:
            return False, "Email is empty"
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not email_pattern.match(email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize user input"""
        # Remove control characters
        sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Limit length if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_json(data: Any) -> tuple[bool, Optional[str]]:
        """Validate JSON data"""
        import json
        
        try:
            if isinstance(data, str):
                json.loads(data)
            else:
                json.dumps(data)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"JSON validation error: {str(e)}"

__all__ = ['InputValidator']