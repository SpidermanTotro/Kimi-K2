"""
Example: Basic Kimi K2 usage
Demonstrates simple chat and tool calling
"""

import os
from kimi_k2 import KimiClient


def example_simple_chat():
    """Example of simple chat interaction."""
    print("=" * 50)
    print("Example 1: Simple Chat")
    print("=" * 50)
    
    # Initialize client
    # Note: Set MOONSHOT_API_KEY environment variable
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    
    # Simple chat
    response = client.simple_chat("What are the key features of Kimi K2?")
    print(f"Response: {response}\n")


def example_tool_calling():
    """Example of tool calling."""
    print("=" * 50)
    print("Example 2: Tool Calling")
    print("=" * 50)
    
    # Define a simple tool
    def get_weather(city: str) -> dict:
        # Simulated weather data
        return {
            "city": city,
            "temperature": "22°C",
            "condition": "Sunny",
            "humidity": "60%"
        }
    
    # Tool definition
    tools = [{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a city",
            "parameters": {
                "type": "object",
                "required": ["city"],
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                }
            }
        }
    }]
    
    tool_map = {"get_weather": get_weather}
    
    # Initialize client
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    
    # Chat with tools
    response = client.tool_chat(
        "What's the weather like in Beijing?",
        tools=tools,
        tool_map=tool_map
    )
    print(f"Response: {response}\n")


def example_structured_conversation():
    """Example of structured conversation."""
    print("=" * 50)
    print("Example 3: Structured Conversation")
    print("=" * 50)
    
    client = KimiClient(api_key=os.getenv("MOONSHOT_API_KEY"))
    
    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "How do I read a file in Python?"},
    ]
    
    response = client.chat(messages, max_tokens=500)
    print(f"Response: {response.choices[0].message.content}\n")


if __name__ == "__main__":
    print("Kimi K2 SDK Examples\n")
    print("Note: Set MOONSHOT_API_KEY environment variable to run these examples\n")
    
    # Check if API key is set
    if not os.getenv("MOONSHOT_API_KEY"):
        print("⚠️  MOONSHOT_API_KEY not set. Examples will not make actual API calls.")
        print("Set it with: export MOONSHOT_API_KEY='your-api-key'\n")
    
    example_simple_chat()
    example_tool_calling()
    example_structured_conversation()
    
    print("Examples completed!")
