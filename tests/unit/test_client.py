"""
Unit tests for KimiClient
"""

import pytest
from unittest.mock import Mock, patch
from kimi_k2.client import KimiClient


class TestKimiClient:
    """Test suite for KimiClient."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        client = KimiClient(
            api_key="test_key",
            base_url="https://test.api.com",
            model="kimi-k2-instruct",
            temperature=0.7
        )
        
        assert client.model == "kimi-k2-instruct"
        assert client.temperature == 0.7
        assert client.default_system_prompt is not None
    
    @patch('kimi_k2.client.OpenAI')
    def test_client_default_values(self, mock_openai):
        """Test client with default values."""
        mock_openai.return_value = Mock()
        
        client = KimiClient(api_key="test_key")
        
        assert client.model == "kimi-k2-instruct"
        assert client.temperature == 0.6
    
    @patch('kimi_k2.client.OpenAI')
    def test_simple_chat(self, mock_openai):
        """Test simple chat functionality."""
        # Setup mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        client = KimiClient(api_key="test_key")
        response = client.simple_chat("Test message")
        
        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('kimi_k2.client.OpenAI')
    def test_chat_with_tools(self, mock_openai):
        """Test chat with tools."""
        # Setup mock
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # First response with tool call
        mock_response1 = Mock()
        mock_response1.choices = [Mock()]
        mock_response1.choices[0].finish_reason = "tool_calls"
        mock_response1.choices[0].message.tool_calls = [Mock()]
        mock_response1.choices[0].message.tool_calls[0].function.name = "test_tool"
        mock_response1.choices[0].message.tool_calls[0].function.arguments = '{"arg": "value"}'
        mock_response1.choices[0].message.tool_calls[0].id = "call_123"
        
        # Second response after tool execution
        mock_response2 = Mock()
        mock_response2.choices = [Mock()]
        mock_response2.choices[0].finish_reason = "stop"
        mock_response2.choices[0].message.content = "Final response"
        
        mock_client.chat.completions.create.side_effect = [mock_response1, mock_response2]
        
        # Test
        client = KimiClient(api_key="test_key")
        
        tools = [{"type": "function", "function": {"name": "test_tool"}}]
        tool_map = {"test_tool": lambda arg: {"result": arg}}
        
        response = client.tool_chat("Test message", tools, tool_map)
        
        assert response == "Final response"
        assert mock_client.chat.completions.create.call_count == 2
    
    @patch('kimi_k2.client.OpenAI')
    def test_chat_with_custom_parameters(self, mock_openai):
        """Test chat with custom parameters."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        client = KimiClient(api_key="test_key")
        
        messages = [{"role": "user", "content": "Test"}]
        client.chat(messages, temperature=0.8, max_tokens=1000)
        
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args["temperature"] == 0.8
        assert call_args["max_tokens"] == 1000
    
    @patch('kimi_k2.client.OpenAI')
    def test_tool_chat_max_iterations(self, mock_openai):
        """Test tool chat respects max iterations."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Always return tool_calls to trigger iteration limit
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].finish_reason = "tool_calls"
        mock_response.choices[0].message.tool_calls = [Mock()]
        mock_response.choices[0].message.tool_calls[0].function.name = "test_tool"
        mock_response.choices[0].message.tool_calls[0].function.arguments = '{}'
        mock_response.choices[0].message.tool_calls[0].id = "call_123"
        
        mock_client.chat.completions.create.return_value = mock_response
        
        client = KimiClient(api_key="test_key")
        
        tools = [{"type": "function", "function": {"name": "test_tool"}}]
        tool_map = {"test_tool": lambda: {}}
        
        response = client.tool_chat("Test", tools, tool_map, max_iterations=3)
        
        assert response == "Maximum tool call iterations reached."
        assert mock_client.chat.completions.create.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
