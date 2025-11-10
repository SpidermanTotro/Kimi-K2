"""Example: Code generation assistant using Kimi-K2."""

from kimi_k2.client import KimiClient
from kimi_k2.tools import ToolManager


def main():
    """Run code generation assistant example."""
    client = KimiClient(
        base_url="http://localhost:8000", model_name="kimi-k2", temperature=0.6
    )

    # Create tools for code assistance
    tool_manager = ToolManager()

    @tool_manager.register(description="Execute Python code and return output")
    def execute_code(code: str) -> dict:
        """Execute Python code safely (simulated)."""
        # In production, use a sandboxed environment
        # This is just a simulation
        return {
            "status": "success",
            "output": "Code execution simulated successfully",
            "code": code,
        }

    @tool_manager.register(description="Search documentation for a topic")
    def search_docs(topic: str) -> dict:
        """Search Python documentation."""
        # Simulated documentation search
        docs = {
            "list comprehension": "List comprehensions provide a concise way to create lists: [x for x in range(10)]",
            "decorators": "Decorators are functions that modify other functions: @decorator\\ndef func(): pass",
            "async": "Async functions use async/await syntax: async def func(): await something()",
        }
        return {
            "topic": topic,
            "content": docs.get(topic.lower(), "No documentation found"),
        }

    print("=== Code Generation Assistant ===\n")

    # Example 1: Generate a function
    print("Example 1: Function Generation")
    print("-" * 50)

    messages = [
        {
            "role": "system",
            "content": "You are an expert Python developer. Write clean, well-documented code.",
        },
        {
            "role": "user",
            "content": "Create a Python function to merge two sorted lists into one sorted list.",
        },
    ]

    response = client.chat(messages)
    print(f"Generated Code:\n{response}\n")

    # Example 2: Code review and improvement
    print("Example 2: Code Review")
    print("-" * 50)

    code_to_review = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
"""

    messages = [
        {
            "role": "system",
            "content": "You are a code reviewer. Provide constructive feedback.",
        },
        {
            "role": "user",
            "content": f"Review this code and suggest improvements:\n\n```python\n{code_to_review}\n```",
        },
    ]

    response = client.chat(messages)
    print(f"Review:\n{response}\n")

    # Example 3: Interactive code generation with tools
    print("Example 3: Interactive Code Generation")
    print("-" * 50)

    messages = [
        {
            "role": "system",
            "content": "You are a coding assistant with access to documentation and code execution.",
        },
        {
            "role": "user",
            "content": "I need help understanding list comprehensions. Search for docs and show me examples.",
        },
    ]

    response = client.chat_with_tools(
        messages=messages,
        tools=tool_manager.get_tool_schemas(),
        tool_map=tool_manager.get_tool_map(),
    )

    print(f"Response:\n{response}\n")

    # Example 4: Multi-language code generation
    print("Example 4: Multi-language Support")
    print("-" * 50)

    messages = [
        {
            "role": "user",
            "content": "Write a function to check if a string is a palindrome in Python, JavaScript, and Go.",
        }
    ]

    response = client.chat(messages)
    print(f"Multi-language Code:\n{response}\n")

    # Example 5: Refactoring
    print("Example 5: Code Refactoring")
    print("-" * 50)

    legacy_code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item * 3)
    return result
"""

    messages = [
        {
            "role": "user",
            "content": f"Refactor this code to be more Pythonic:\n\n```python\n{legacy_code}\n```",
        }
    ]

    response = client.chat(messages)
    print(f"Refactored Code:\n{response}\n")


if __name__ == "__main__":
    main()
