"""Example: Tool calling with Kimi-K2."""

import json
from kimi_k2.client import KimiClient
from kimi_k2.tools import ToolManager


def main():
    """Run tool calling example."""
    # Initialize client
    client = KimiClient(
        base_url="http://localhost:8000", api_key="dummy", model_name="kimi-k2"
    )

    # Create tool manager
    tool_manager = ToolManager()

    # Register tools using decorator
    @tool_manager.register(description="Get current weather for a city")
    def get_weather(city: str) -> dict:
        """Get weather information for a city."""
        # Simulated weather data
        weather_data = {
            "Beijing": {"temperature": 22, "condition": "Sunny"},
            "Shanghai": {"temperature": 28, "condition": "Cloudy"},
            "London": {"temperature": 15, "condition": "Rainy"},
            "New York": {"temperature": 18, "condition": "Partly Cloudy"},
        }
        return weather_data.get(city, {"temperature": 20, "condition": "Unknown"})

    @tool_manager.register(description="Search for information")
    def search(query: str) -> dict:
        """Search for information."""
        # Simulated search results
        return {
            "query": query,
            "results": [
                f"Result 1 for '{query}'",
                f"Result 2 for '{query}'",
                f"Result 3 for '{query}'",
            ],
        }

    @tool_manager.register(description="Calculate mathematical expression")
    def calculate(expression: str) -> dict:
        """Evaluate a mathematical expression."""
        try:
            result = eval(expression, {"__builtins__": {}})
            return {"result": result, "expression": expression}
        except Exception as e:
            return {"error": str(e), "expression": expression}

    print("=== Tool Calling Example ===\n")

    # Example 1: Weather query
    print("Example 1: Weather Query")
    print("-" * 50)

    messages = [
        {
            "role": "system",
            "content": "You are Kimi, an AI assistant created by Moonshot AI.",
        },
        {
            "role": "user",
            "content": "What's the weather like in Beijing today? Use the tool to check.",
        },
    ]

    response = client.chat_with_tools(
        messages=messages,
        tools=tool_manager.get_tool_schemas(),
        tool_map=tool_manager.get_tool_map(),
    )

    print(f"Final Response: {response}\n")

    # Example 2: Multiple tool calls
    print("Example 2: Multiple Tool Calls")
    print("-" * 50)

    messages = [
        {
            "role": "user",
            "content": "Calculate 15 * 23 and then search for 'Kimi K2 model'",
        }
    ]

    response = client.chat_with_tools(
        messages=messages,
        tools=tool_manager.get_tool_schemas(),
        tool_map=tool_manager.get_tool_map(),
    )

    print(f"Final Response: {response}\n")

    # Example 3: Manual tool definition
    print("Example 3: Manual Tool Definition")
    print("-" * 50)

    def get_user_info(user_id: int) -> dict:
        """Get user information."""
        return {
            "user_id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
        }

    manual_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_user_info",
                "description": "Retrieve user information by ID",
                "parameters": {
                    "type": "object",
                    "required": ["user_id"],
                    "properties": {
                        "user_id": {"type": "integer", "description": "The user's ID"}
                    },
                },
            },
        }
    ]

    manual_tool_map = {"get_user_info": get_user_info}

    messages = [{"role": "user", "content": "Get information for user ID 42"}]

    response = client.chat_with_tools(
        messages=messages, tools=manual_tools, tool_map=manual_tool_map
    )

    print(f"Final Response: {response}\n")


if __name__ == "__main__":
    main()
