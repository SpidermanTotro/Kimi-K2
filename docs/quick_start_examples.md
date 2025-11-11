# Quick Start Examples for Kimi K2

This guide provides simple, ready-to-run examples to get started with Kimi K2 quickly. Perfect for developers who want to see the AI in action immediately.

## Table of Contents
- [Setup](#setup)
- [Basic Chat](#basic-chat)
- [Code Generation](#code-generation)
- [Code Review](#code-review)
- [Problem Solving](#problem-solving)
- [Multi-Language Support](#multi-language-support)

---

## Setup

First, ensure you have Kimi K2 running locally or access to the API:

```python
from openai import OpenAI

# For local deployment
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"  # Not needed for local deployment
)

# For Moonshot AI API
# client = OpenAI(
#     base_url="https://platform.moonshot.ai/v1",
#     api_key="your-api-key-here"
# )

MODEL_NAME = "kimi-k2"
```

---

## Basic Chat

### Simple Conversation

```python
def simple_chat():
    """Basic chat interaction with Kimi K2."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are Kimi, an AI assistant created by Moonshot AI."},
            {"role": "user", "content": "Explain what makes you unique as an AI assistant."}
        ],
        temperature=0.6,
        max_tokens=300
    )
    
    print(response.choices[0].message.content)

simple_chat()
```

**Expected Output:**
```
As Kimi, I'm a state-of-the-art AI assistant built on the K2 model by Moonshot AI. What makes me unique is:

1. Agentic Intelligence: I can autonomously plan and execute multi-step tasks
2. Advanced Tool Use: I can intelligently integrate with external tools and APIs
3. Strong Reasoning: I excel at complex problem-solving and logical reasoning
4. Coding Excellence: I have exceptional capabilities in code generation, review, and debugging
5. Large Context: I can handle up to 128K tokens of context

I'm designed specifically for agentic applications, making me ideal for autonomous problem-solving tasks.
```

---

## Code Generation

### Example 1: Generate a Function

```python
def generate_code():
    """Ask Kimi K2 to generate a specific function."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": """
Write a Python function that:
1. Takes a list of numbers
2. Removes duplicates
3. Sorts in descending order
4. Returns the top N values

Include type hints, docstring, and example usage.
"""}
        ],
        temperature=0.4,
        max_tokens=500
    )
    
    print(response.choices[0].message.content)

generate_code()
```

**Expected Output:**
```python
from typing import List

def get_top_n_unique(numbers: List[float], n: int) -> List[float]:
    """
    Get the top N unique values from a list of numbers.
    
    Args:
        numbers: List of numeric values
        n: Number of top values to return
        
    Returns:
        List of top N unique values in descending order
        
    Examples:
        >>> get_top_n_unique([5, 2, 8, 2, 9, 1, 8], 3)
        [9, 8, 5]
        >>> get_top_n_unique([1, 1, 1], 2)
        [1]
    """
    # Remove duplicates by converting to set, then sort in descending order
    unique_sorted = sorted(set(numbers), reverse=True)
    
    # Return top N values
    return unique_sorted[:n]

# Example usage
numbers = [5, 2, 8, 2, 9, 1, 8, 3, 9, 7]
print(get_top_n_unique(numbers, 5))  # Output: [9, 8, 7, 5, 3]
```

### Example 2: Generate a Class

```python
def generate_class():
    """Ask Kimi K2 to generate a complete class."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": """
Create a Python class for a simple shopping cart with:
- Add item (with quantity)
- Remove item
- Calculate total
- Apply discount
Include proper error handling.
"""}
        ],
        temperature=0.4,
        max_tokens=800
    )
    
    print(response.choices[0].message.content)

generate_class()
```

---

## Code Review

### Example 1: Review and Improve Code

```python
def review_code():
    """Ask Kimi K2 to review code and suggest improvements."""
    code_to_review = """
def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total = total + numbers[i]
    return total / len(numbers)
"""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": f"""
Review this code and provide:
1. Issues or potential bugs
2. Suggestions for improvement
3. Improved version

Code:
{code_to_review}
"""}
        ],
        temperature=0.4,
        max_tokens=600
    )
    
    print(response.choices[0].message.content)

review_code()
```

**Expected Output:**
```
Issues and Improvements:

1. **Bug**: Division by zero error if the list is empty
2. **Inefficiency**: Using index-based loop instead of direct iteration
3. **Missing validation**: No type checking or input validation
4. **No documentation**: Missing docstring

Improved Version:

```python
def calculate_average(numbers: list[float]) -> float:
    """
    Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numeric values
        
    Returns:
        The average of the numbers
        
    Raises:
        ValueError: If the list is empty or contains non-numeric values
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    if not all(isinstance(n, (int, float)) for n in numbers):
        raise ValueError("All elements must be numeric")
    
    return sum(numbers) / len(numbers)
```

Improvements made:
- ✅ Added input validation for empty list
- ✅ Added type checking
- ✅ Used built-in sum() for efficiency
- ✅ Added type hints and comprehensive docstring
- ✅ Added proper error handling
```

### Example 2: Find Security Issues

```python
def find_security_issues():
    """Ask Kimi K2 to identify security vulnerabilities."""
    code = """
def login(username, password):
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    result = database.execute(query)
    return result
"""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": f"""
Analyze this code for security vulnerabilities:

{code}

Provide:
1. Security issues found
2. Why they're dangerous
3. Secure alternative
"""}
        ],
        temperature=0.3,
        max_tokens=600
    )
    
    print(response.choices[0].message.content)

find_security_issues()
```

---

## Problem Solving

### Example 1: Algorithm Design

```python
def solve_algorithm_problem():
    """Ask Kimi K2 to solve an algorithmic problem."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": """
Problem: Given an array of integers, find two numbers that add up to a target sum.

Requirements:
- Return the indices of the two numbers
- Each input has exactly one solution
- Can't use the same element twice

Example:
Input: nums = [2, 7, 11, 15], target = 9
Output: [0, 1] (because nums[0] + nums[1] = 2 + 7 = 9)

Provide:
1. Solution approach
2. Time/space complexity analysis
3. Python implementation
"""}
        ],
        temperature=0.4,
        max_tokens=800
    )
    
    print(response.choices[0].message.content)

solve_algorithm_problem()
```

### Example 2: Debugging Help

```python
def debug_code():
    """Ask Kimi K2 to help debug problematic code."""
    buggy_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-1)

print(fibonacci(10))  # Expected: 55, but getting wrong result
"""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": f"""
This code is not producing the correct Fibonacci number. 

{buggy_code}

Please:
1. Identify the bug
2. Explain why it's wrong
3. Provide the corrected version
"""}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    print(response.choices[0].message.content)

debug_code()
```

---

## Multi-Language Support

### JavaScript/TypeScript Example

```python
def generate_javascript():
    """Generate JavaScript/TypeScript code."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": """
Create a TypeScript class for managing a simple todo list with:
- Add todo
- Mark as complete
- Delete todo
- Get all todos
- Get active/completed todos

Use proper TypeScript types and interfaces.
"""}
        ],
        temperature=0.4,
        max_tokens=800
    )
    
    print(response.choices[0].message.content)

generate_javascript()
```

### Java Example

```python
def generate_java():
    """Generate Java code."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": """
Create a Java class for a generic Stack data structure with:
- push
- pop
- peek
- isEmpty
- size

Include proper error handling and generics.
"""}
        ],
        temperature=0.4,
        max_tokens=800
    )
    
    print(response.choices[0].message.content)

generate_java()
```

### Go Example

```python
def generate_go():
    """Generate Go code."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": """
Create a Go program that:
1. Reads a CSV file
2. Processes data concurrently using goroutines
3. Writes results to a new CSV file

Include proper error handling and context management.
"""}
        ],
        temperature=0.4,
        max_tokens=1000
    )
    
    print(response.choices[0].message.content)

generate_go()
```

### Rust Example

```python
def generate_rust():
    """Generate Rust code."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": """
Create a Rust struct for a simple HTTP client that:
- Makes GET/POST requests
- Handles errors properly
- Uses async/await
- Has proper lifetime annotations

Include example usage.
"""}
        ],
        temperature=0.4,
        max_tokens=1000
    )
    
    print(response.choices[0].message.content)

generate_rust()
```

---

## Streaming Responses

For real-time output (useful for long responses):

```python
def streaming_example():
    """Example of streaming responses from Kimi K2."""
    print("Streaming response:\n")
    
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": "Write a comprehensive guide on Python list comprehensions with 5 examples."}
        ],
        temperature=0.6,
        max_tokens=1000,
        stream=True  # Enable streaming
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end='', flush=True)
    
    print("\n\nStreaming complete!")

streaming_example()
```

---

## Batch Processing

Process multiple requests efficiently:

```python
import asyncio
import aiohttp

async def batch_code_review(code_snippets: list[str]):
    """Review multiple code snippets concurrently."""
    
    async def review_single(code: str) -> str:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": f"Review this code briefly:\n{code}"}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content
    
    # Process all reviews concurrently
    tasks = [review_single(code) for code in code_snippets]
    results = await asyncio.gather(*tasks)
    
    return results

# Example usage
codes = [
    "def add(a, b): return a + b",
    "def multiply(x, y): return x * y",
    "def divide(a, b): return a / b"
]

# asyncio.run(batch_code_review(codes))
```

---

## Advanced: Custom System Prompts

Customize Kimi K2's behavior with system prompts:

```python
def custom_assistant():
    """Create a custom-behaving assistant."""
    
    # Example: Code review assistant
    system_prompt = """You are an expert code reviewer specializing in Python.
    
Your review style:
- Always mention at least 3 specific improvements
- Focus on performance, readability, and maintainability
- Suggest best practices
- Point out potential bugs
- Keep responses concise and actionable
"""
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Review this: def calc(x, y): return x + y"}
        ],
        temperature=0.4,
        max_tokens=400
    )
    
    print(response.choices[0].message.content)

custom_assistant()
```

---

## Best Practices

1. **Temperature Settings**:
   - `0.3-0.4`: For code generation and factual tasks
   - `0.6`: For general chat (recommended default)
   - `0.7-0.9`: For creative tasks

2. **Token Limits**:
   - Set appropriate `max_tokens` based on expected response length
   - Kimi K2 supports up to 128K context length

3. **Error Handling**:
   ```python
   try:
       response = client.chat.completions.create(...)
   except Exception as e:
       print(f"Error: {e}")
   ```

4. **Context Management**:
   - Keep conversation history for multi-turn chats
   - Clear context when switching topics

---

## Next Steps

- Explore the [Complete Examples Guide](examples_guide.md) for more advanced use cases
- Learn about [Tool Calling](tool_call_guidance.md) for agentic workflows
- Check out [Deployment Options](deploy_guidance.md) for production use

For more information, visit the [main README](../README.md).
