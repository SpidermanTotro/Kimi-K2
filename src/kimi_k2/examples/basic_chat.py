"""Example: Basic chat completion with Kimi-K2."""

from kimi_k2.client import KimiClient


def main():
    """Run basic chat example."""
    # Initialize client
    # Replace with your actual service URL
    client = KimiClient(
        base_url="http://localhost:8000",
        api_key="dummy",  # Use actual API key if required
        model_name="kimi-k2",
        temperature=0.6,
    )

    print("=== Simple Chat Example ===\n")

    # Simple one-turn chat
    response = client.simple_chat(
        user_message="What are the key features of Kimi K2?",
        system_message="You are Kimi, an AI assistant created by Moonshot AI.",
    )

    print(f"Response: {response}\n")

    # Multi-turn conversation
    print("=== Multi-turn Conversation ===\n")

    messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to calculate factorial."},
    ]

    response = client.chat(messages)
    print(f"Assistant: {response}\n")

    # Continue conversation
    messages.append({"role": "assistant", "content": response})
    messages.append({"role": "user", "content": "Now add type hints and docstring."})

    response = client.chat(messages)
    print(f"Assistant: {response}\n")

    # Streaming example
    print("=== Streaming Response ===\n")

    messages = [
        {
            "role": "user",
            "content": "Explain what a transformer is in machine learning.",
        }
    ]

    print("Assistant: ", end="", flush=True)
    for chunk in client.chat(messages, stream=True):
        print(chunk, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    main()
