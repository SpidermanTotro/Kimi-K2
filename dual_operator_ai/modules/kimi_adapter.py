"""
Kimi-K2 Integration Module

Provides seamless integration with Kimi-K2 API for the dual-operator AI system.
"""

from typing import Dict, List, Any, Optional
import json
from openai import OpenAI


class KimiK2Adapter:
    """
    Adapter for integrating with Kimi-K2 API.
    
    This adapter provides a bridge between the dual-operator engine
    and the Kimi-K2 model API.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.moonshot.cn/v1",
        model_name: str = "moonshotai/Kimi-K2-Instruct",
        temperature: float = 0.6
    ):
        """
        Initialize the Kimi-K2 adapter.
        
        Args:
            api_key: API key for Kimi-K2
            base_url: Base URL for the API
            model_name: Name of the model to use
            temperature: Temperature for generation
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.temperature = temperature
        
    def generate_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a response using Kimi-K2.
        
        Args:
            messages: List of message dictionaries
            tools: Optional tool definitions
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Response dictionary
        """
        params = {
            'model': self.model_name,
            'messages': messages,
            'temperature': self.temperature,
            'max_tokens': max_tokens,
            'stream': stream
        }
        
        if tools:
            params['tools'] = tools
            params['tool_choice'] = 'auto'
        
        response = self.client.chat.completions.create(**params)
        
        if stream:
            return {'stream': response}
        else:
            return {
                'content': response.choices[0].message.content,
                'finish_reason': response.choices[0].finish_reason,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
    
    def generate_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_map: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a response with tool calling support.
        
        Args:
            messages: List of message dictionaries
            tools: Tool definitions
            tool_map: Mapping of tool names to implementations
            
        Returns:
            Final response after tool calls
        """
        conversation = messages.copy()
        max_iterations = 5
        iterations = 0
        
        while iterations < max_iterations:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=conversation,
                temperature=self.temperature,
                tools=tools,
                tool_choice='auto'
            )
            
            choice = response.choices[0]
            finish_reason = choice.finish_reason
            
            if finish_reason == 'tool_calls':
                conversation.append(choice.message)
                
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool
                    if tool_name in tool_map:
                        tool_result = tool_map[tool_name](**tool_args)
                    else:
                        tool_result = {'error': f'Tool {tool_name} not found'}
                    
                    conversation.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'name': tool_name,
                        'content': json.dumps(tool_result)
                    })
            else:
                return {
                    'content': choice.message.content,
                    'finish_reason': finish_reason,
                    'iterations': iterations + 1,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                }
            
            iterations += 1
        
        return {
            'content': 'Max iterations reached',
            'finish_reason': 'max_iterations',
            'iterations': iterations
        }
    
    def stream_response(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 2048
    ):
        """
        Stream a response from Kimi-K2.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
