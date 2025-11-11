"""
Kimi K2 Client
Main client for interacting with Kimi K2 model
"""

from typing import Dict, List, Optional, Any
from openai import OpenAI


class KimiClient:
    """
    Enhanced Kimi K2 client with Moon AI integration capabilities.
    
    This client provides a unified interface for accessing Kimi K2's
    advanced features including reasoning, tool calling, and AI integrations.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://platform.moonshot.ai/v1",
        model: str = "kimi-k2-instruct",
        temperature: float = 0.6,
    ):
        """
        Initialize the Kimi K2 client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for the API endpoint
            model: Model identifier (kimi-k2-instruct or kimi-k2-base)
            temperature: Temperature for response generation (default: 0.6)
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.default_system_prompt = "You are Kimi, an AI assistant created by Moonshot AI."
    
    def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: int = 2048,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Any:
        """
        Send a chat completion request.
        
        Args:
            messages: List of message dictionaries
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            tools: Optional list of tool definitions
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Chat completion response
        """
        temp = temperature if temperature is not None else self.temperature
        
        completion_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tokens,
            "stream": stream,
            **kwargs
        }
        
        if tools:
            completion_kwargs["tools"] = tools
            completion_kwargs["tool_choice"] = "auto"
        
        return self.client.chat.completions.create(**completion_kwargs)
    
    def simple_chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Simple chat interface for quick interactions.
        
        Args:
            user_message: User's message
            system_prompt: Optional system prompt override
            
        Returns:
            Model's response as a string
        """
        messages = [
            {"role": "system", "content": system_prompt or self.default_system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self.chat(messages, stream=False)
        return response.choices[0].message.content
    
    def tool_chat(
        self,
        user_message: str,
        tools: List[Dict],
        tool_map: Dict[str, Any],
        system_prompt: Optional[str] = None,
        max_iterations: int = 10,
    ) -> str:
        """
        Chat with automatic tool calling support.
        
        Args:
            user_message: User's message
            tools: List of tool definitions
            tool_map: Mapping of tool names to implementations
            system_prompt: Optional system prompt override
            max_iterations: Maximum number of tool call iterations
            
        Returns:
            Final response after tool executions
        """
        import json
        
        messages = [
            {"role": "system", "content": system_prompt or self.default_system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        iteration = 0
        while iteration < max_iterations:
            response = self.chat(messages, tools=tools, stream=False)
            choice = response.choices[0]
            finish_reason = choice.finish_reason
            
            if finish_reason != "tool_calls":
                return choice.message.content
            
            # Process tool calls
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_func = tool_map.get(tool_name)
                
                if tool_func:
                    tool_result = tool_func(**tool_args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result)
                    })
            
            iteration += 1
        
        return "Maximum tool call iterations reached."
