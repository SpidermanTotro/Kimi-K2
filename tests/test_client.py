"""Test suite for Kimi-K2 client."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from kimi_k2.client import KimiClient


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch("kimi_k2.client.OpenAI") as mock:
        yield mock


@pytest.fixture
def client(mock_openai_client):
    """Create a test client."""
    return KimiClient(
        base_url="http://test:8000", api_key="test-key", model_name="test-model"
    )


class TestKimiClient:
    """Test cases for KimiClient."""

    def test_initialization(self, client):
        """Test client initialization."""
        assert client.model_name == "test-model"
        assert client.temperature == 0.6
        assert client.max_tokens == 2048

    def test_simple_chat(self, client, mock_openai_client):
        """Test simple chat method."""
        # Mock response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"

        client.client.chat.completions.create = Mock(return_value=mock_response)

        # Call simple_chat
        response = client.simple_chat("Hello")

        assert response == "Test response"
        client.client.chat.completions.create.assert_called_once()

    def test_simple_chat_with_system_message(self, client, mock_openai_client):
        """Test simple chat with system message."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"

        client.client.chat.completions.create = Mock(return_value=mock_response)

        response = client.simple_chat("Hello", system_message="You are a bot")

        assert response == "Test response"

        # Verify messages include system message
        call_args = client.client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_chat_streaming(self, client, mock_openai_client):
        """Test streaming chat."""
        # Mock streaming response
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello"))]),
            Mock(choices=[Mock(delta=Mock(content=" world"))]),
            Mock(choices=[Mock(delta=Mock(content=None))]),
        ]

        client.client.chat.completions.create = Mock(return_value=iter(mock_chunks))

        # Call chat with streaming
        result = list(client.chat([{"role": "user", "content": "Test"}], stream=True))

        assert result == ["Hello", " world"]

    def test_chat_with_tools(self, client, mock_openai_client):
        """Test chat with tools."""
        # Mock first response with tool call
        mock_response_1 = Mock()
        mock_response_1.choices = [Mock()]
        mock_response_1.choices[0].finish_reason = "tool_calls"
        mock_response_1.choices[0].message = Mock()

        # Mock tool call
        mock_tool_call = Mock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "test_tool"
        mock_tool_call.function.arguments = '{"arg": "value"}'

        mock_response_1.choices[0].message.tool_calls = [mock_tool_call]

        # Mock second response (final)
        mock_response_2 = Mock()
        mock_response_2.choices = [Mock()]
        mock_response_2.choices[0].finish_reason = "stop"
        mock_response_2.choices[0].message.content = "Final response"

        client.client.chat.completions.create = Mock(
            side_effect=[mock_response_1, mock_response_2]
        )

        # Mock tool
        test_tool = Mock(return_value={"result": "success"})
        tool_map = {"test_tool": test_tool}
        tools = [{"type": "function", "function": {"name": "test_tool"}}]

        # Call chat_with_tools
        response = client.chat_with_tools(
            messages=[{"role": "user", "content": "Test"}],
            tools=tools,
            tool_map=tool_map,
        )

        assert response == "Final response"
        test_tool.assert_called_once_with(arg="value")

    def test_chat_with_custom_temperature(self, client, mock_openai_client):
        """Test chat with custom temperature."""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Response"

        client.client.chat.completions.create = Mock(return_value=mock_response)

        client.chat([{"role": "user", "content": "Test"}], temperature=0.9)

        call_args = client.client.chat.completions.create.call_args
        assert call_args.kwargs["temperature"] == 0.9

    def test_chat_with_tools_max_iterations(self, client, mock_openai_client):
        """Test chat with tools reaches max iterations."""
        # Always return tool_calls
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].finish_reason = "tool_calls"
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.tool_calls = []

        client.client.chat.completions.create = Mock(return_value=mock_response)

        response = client.chat_with_tools(
            messages=[{"role": "user", "content": "Test"}],
            tools=[],
            tool_map={},
            max_iterations=3,
        )

        assert "Maximum tool calling iterations reached" in response
        assert client.client.chat.completions.create.call_count == 3
