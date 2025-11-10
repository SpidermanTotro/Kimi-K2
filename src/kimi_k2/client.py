"""Enhanced client for Kimi-K2 with additional utilities."""

import json
from typing import Any, Dict, List, Optional, Union, Iterator
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class KimiClient:
    """Enhanced client for interacting with Kimi-K2 models.

    This client provides convenient methods for common operations
    including chat completion, tool calling, and streaming.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str = "dummy",
        model_name: str = "kimi-k2",
        temperature: float = 0.6,
        max_tokens: int = 2048,
    ):
        """Initialize the Kimi client.

        Args:
            base_url: Base URL of the Kimi-K2 service
            api_key: API key (default: "dummy" for local deployments)
            model_name: Model name to use
            temperature: Sampling temperature (recommended: 0.6)
            max_tokens: Maximum tokens to generate
        """
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[str, Iterator[str]]:
        """Send a chat completion request.

        Args:
            messages: List of message dictionaries
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API

        Returns:
            Response content as string, or iterator if streaming
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temp,
            max_tokens=max_tok,
            stream=stream,
            **kwargs,
        )

        if stream:
            return self._stream_response(response)
        else:
            return response.choices[0].message.content

    def _stream_response(self, response) -> Iterator[str]:
        """Stream response chunks."""
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_map: Dict[str, callable],
        max_iterations: int = 10,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """Chat with automatic tool calling.

        Args:
            messages: List of message dictionaries
            tools: List of tool definitions
            tool_map: Dictionary mapping tool names to callable functions
            max_iterations: Maximum number of tool call iterations
            temperature: Override default temperature
            **kwargs: Additional parameters

        Returns:
            Final response content
        """
        temp = temperature if temperature is not None else self.temperature
        current_messages = messages.copy()

        for iteration in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=current_messages,
                temperature=temp,
                tools=tools,
                tool_choice="auto",
                **kwargs,
            )

            choice = response.choices[0]
            finish_reason = choice.finish_reason

            if finish_reason != "tool_calls":
                return choice.message.content

            # Process tool calls
            current_messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

                if tool_name not in tool_map:
                    logger.error(f"Tool {tool_name} not found in tool_map")
                    continue

                try:
                    tool_result = tool_map[tool_name](**tool_args)

                    current_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(tool_result),
                        }
                    )
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}")
                    current_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps({"error": str(e)}),
                        }
                    )

        logger.warning(f"Reached max iterations ({max_iterations})")
        return "Maximum tool calling iterations reached."

    def simple_chat(
        self, user_message: str, system_message: Optional[str] = None
    ) -> str:
        """Simple one-turn chat.

        Args:
            user_message: User's message
            system_message: Optional system message

        Returns:
            Model's response
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": user_message})

        return self.chat(messages)
