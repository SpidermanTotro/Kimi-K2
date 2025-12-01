"""
NEXUS AI - GPT Model Handler
Handles GPT-4, GPT-4 Turbo, and GPT-4 Vision models
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional
from config.settings import config
from utils.logger import get_logger

logger = get_logger(__name__)

class GPTHandler:
    """Handler for OpenAI GPT models"""
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Initialize GPT handler
        
        Args:
            model: Model name (defaults to config.DEFAULT_CHAT_MODEL)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
        """
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = model or config.DEFAULT_CHAT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        logger.info(f"Initialized GPTHandler with model: {self.model}")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            stream: Enable streaming responses
        
        Returns:
            Dict with response content and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=stream
            )
            
            if stream:
                return {"stream": response}
            
            result = {
                "content": response.choices[0].message.content,
                "role": response.choices[0].message.role,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.debug(f"Chat completion: {result['usage']['total_tokens']} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Chat completion error: {str(e)}")
            return {
                "error": str(e),
                "content": f"Error: {str(e)}"
            }
    
    def chat_with_system(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Chat with system prompt and optional history
        
        Args:
            user_message: User's message
            system_prompt: System prompt to set behavior
            conversation_history: Previous messages
        
        Returns:
            Dict with response content and metadata
        """
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat(messages)
    
    def vision_chat(
        self,
        text: str,
        image_url: str,
        detail: str = "auto"
    ) -> Dict[str, Any]:
        """
        Chat with vision capabilities (image understanding)
        
        Args:
            text: Text prompt/question about the image
            image_url: URL or base64 encoded image
            detail: Level of detail ('low', 'high', 'auto')
        
        Returns:
            Dict with response content and metadata
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": detail
                            }
                        }
                    ]
                }
            ]
            
            # Use vision model
            original_model = self.model
            self.model = config.GPT_4_VISION
            
            result = self.chat(messages)
            
            # Restore original model
            self.model = original_model
            
            return result
            
        except Exception as e:
            logger.error(f"Vision chat error: {str(e)}")
            return {
                "error": str(e),
                "content": f"Vision error: {str(e)}"
            }
    
    def function_call(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        function_call: str = "auto"
    ) -> Dict[str, Any]:
        """
        Chat with function calling
        
        Args:
            messages: Conversation messages
            functions: Available functions
            function_call: How to call functions ('auto', 'none', or specific function)
        
        Returns:
            Dict with response and function call info
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call=function_call
            )
            
            choice = response.choices[0]
            
            result = {
                "content": choice.message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": choice.finish_reason
            }
            
            # Add function call info if present
            if choice.message.function_call:
                result["function_call"] = {
                    "name": choice.message.function_call.name,
                    "arguments": choice.message.function_call.arguments
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Function call error: {str(e)}")
            return {
                "error": str(e),
                "content": f"Function call error: {str(e)}"
            }

__all__ = ['GPTHandler']