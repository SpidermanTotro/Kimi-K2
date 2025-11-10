# Tutorials

Step-by-step tutorials for using Kimi-K2 utilities and examples.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Tutorial 1: Basic Chat Application](#tutorial-1-basic-chat-application)
3. [Tutorial 2: Building a Tool-Using Agent](#tutorial-2-building-a-tool-using-agent)
4. [Tutorial 3: Code Generation Assistant](#tutorial-3-code-generation-assistant)
5. [Tutorial 4: Multi-Agent System](#tutorial-4-multi-agent-system)
6. [Tutorial 5: Performance Benchmarking](#tutorial-5-performance-benchmarking)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A running Kimi-K2 service (see [deployment guide](deploy_guidance.md))

### Installation

Install the Kimi-K2 utilities:

```bash
cd Kimi-K2
pip install -e .
```

For development with testing tools:

```bash
pip install -e ".[dev]"
```

For all examples:

```bash
pip install -e ".[dev,examples]"
```

### Verify Installation

```bash
# Test the CLI
kimi-cli --version

# Quick test
kimi-cli chat --url http://localhost:8000 "Hello, Kimi!"
```

---

## Tutorial 1: Basic Chat Application

Learn to build a simple chat application.

### Step 1: Initialize the Client

Create a new file `my_chat.py`:

```python
from kimi_k2.client import KimiClient

# Initialize client with your service URL
client = KimiClient(
    base_url="http://localhost:8000",
    api_key="dummy",  # Change if using API key authentication
    temperature=0.6
)
```

### Step 2: Simple One-Turn Chat

```python
# Ask a simple question
response = client.simple_chat("What is Python?")
print(response)
```

### Step 3: Multi-Turn Conversation

```python
# Start a conversation
messages = [
    {"role": "system", "content": "You are a helpful programming tutor."},
    {"role": "user", "content": "I want to learn Python. Where should I start?"}
]

response = client.chat(messages)
print(f"Assistant: {response}\n")

# Continue the conversation
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": "Can you recommend some beginner projects?"})

response = client.chat(messages)
print(f"Assistant: {response}")
```

### Step 4: Add Streaming

```python
# Stream the response for better UX
messages = [
    {"role": "user", "content": "Write a story about a robot learning to code."}
]

print("Assistant: ", end="", flush=True)
for chunk in client.chat(messages, stream=True):
    print(chunk, end="", flush=True)
print("\n")
```

### Complete Example

```python
from kimi_k2.client import KimiClient

def main():
    client = KimiClient(base_url="http://localhost:8000")
    
    print("=== Kimi Chat Application ===\n")
    
    # Initialize conversation
    messages = [
        {"role": "system", "content": "You are a friendly AI assistant."}
    ]
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        messages.append({"role": "user", "content": user_input})
        
        print("\nKimi: ", end="", flush=True)
        response = ""
        for chunk in client.chat(messages, stream=True):
            print(chunk, end="", flush=True)
            response += chunk
        print()
        
        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
```

---

## Tutorial 2: Building a Tool-Using Agent

Create an agent that can use tools to answer questions.

### Step 1: Define Your Tools

```python
from kimi_k2.tools import ToolManager

tool_manager = ToolManager()

@tool_manager.register(description="Get current weather for a city")
def get_weather(city: str) -> dict:
    """Get weather information."""
    # In production, call a real weather API
    return {
        "city": city,
        "temperature": 22,
        "condition": "Sunny",
        "humidity": 60
    }

@tool_manager.register(description="Search the web for information")
def web_search(query: str, num_results: int = 3) -> dict:
    """Search for information."""
    # In production, call a real search API
    return {
        "query": query,
        "results": [
            f"Result 1 about {query}",
            f"Result 2 about {query}",
            f"Result 3 about {query}"
        ][:num_results]
    }

@tool_manager.register(description="Get the current time")
def get_current_time() -> dict:
    """Get current time."""
    from datetime import datetime
    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "UTC"
    }
```

### Step 2: Use Tools in Conversation

```python
from kimi_k2.client import KimiClient

client = KimiClient(base_url="http://localhost:8000")

# Ask a question that requires tools
messages = [
    {"role": "system", "content": "You are a helpful assistant with access to tools."},
    {"role": "user", "content": "What's the weather like in Tokyo? Also, what time is it now?"}
]

response = client.chat_with_tools(
    messages=messages,
    tools=tool_manager.get_tool_schemas(),
    tool_map=tool_manager.get_tool_map()
)

print(f"Response: {response}")
```

### Step 3: Create an Interactive Agent

```python
def run_agent():
    """Run an interactive tool-using agent."""
    client = KimiClient(base_url="http://localhost:8000")
    
    messages = [
        {"role": "system", "content": 
         "You are a helpful assistant. Use tools when needed to provide accurate information."}
    ]
    
    print("=== Kimi Tool Agent ===")
    print("Available tools: weather, search, time")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat_with_tools(
            messages=messages,
            tools=tool_manager.get_tool_schemas(),
            tool_map=tool_manager.get_tool_map()
        )
        
        print(f"Agent: {response}\n")
        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_agent()
```

---

## Tutorial 3: Code Generation Assistant

Build a specialized code generation assistant.

### Step 1: Set Up the Assistant

```python
from kimi_k2.client import KimiClient

client = KimiClient(
    base_url="http://localhost:8000",
    temperature=0.6  # Good balance for code generation
)

system_message = """
You are an expert software engineer. When writing code:
1. Write clean, well-documented code
2. Include type hints where appropriate
3. Add docstrings for functions and classes
4. Follow best practices
5. Explain your code briefly
"""
```

### Step 2: Generate Code

```python
def generate_code(task: str) -> str:
    """Generate code for a given task."""
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Write Python code to: {task}"}
    ]
    
    return client.chat(messages)

# Example usage
task = "implement a binary search function"
code = generate_code(task)
print(code)
```

### Step 3: Add Code Review

```python
def review_code(code: str) -> str:
    """Review and suggest improvements for code."""
    messages = [
        {"role": "system", "content": "You are a code reviewer. Provide constructive feedback."},
        {"role": "user", "content": f"Review this code:\n\n```python\n{code}\n```"}
    ]
    
    return client.chat(messages)

# Example
original_code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
"""

review = review_code(original_code)
print(f"Review:\n{review}")
```

### Step 4: Complete Workflow

```python
class CodeAssistant:
    """Complete code generation and review assistant."""
    
    def __init__(self, client):
        self.client = client
    
    def generate(self, task: str, language: str = "Python") -> str:
        """Generate code for a task."""
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Write {language} code to: {task}"}
        ]
        return self.client.chat(messages)
    
    def review(self, code: str) -> str:
        """Review code."""
        messages = [
            {"role": "system", "content": "You are an expert code reviewer."},
            {"role": "user", "content": f"Review:\n```\n{code}\n```"}
        ]
        return self.client.chat(messages)
    
    def refactor(self, code: str, goal: str = "improve readability") -> str:
        """Refactor code."""
        messages = [
            {"role": "user", "content": 
             f"Refactor this code to {goal}:\n```\n{code}\n```"}
        ]
        return self.client.chat(messages)
    
    def explain(self, code: str) -> str:
        """Explain code."""
        messages = [
            {"role": "user", "content": f"Explain this code:\n```\n{code}\n```"}
        ]
        return self.client.chat(messages)

# Usage
assistant = CodeAssistant(client)

# Generate
code = assistant.generate("implement a LRU cache")
print(f"Generated:\n{code}\n")

# Review
review = assistant.review(code)
print(f"Review:\n{review}\n")

# Explain
explanation = assistant.explain(code)
print(f"Explanation:\n{explanation}")
```

---

## Tutorial 4: Multi-Agent System

Create a system with multiple AI agents.

### Step 1: Define Agent Class

```python
from kimi_k2.client import KimiClient
from typing import List, Dict

class Agent:
    """An AI agent with a specific role."""
    
    def __init__(self, name: str, role: str, client: KimiClient):
        self.name = name
        self.role = role
        self.client = client
        self.history = []
    
    def respond(self, message: str) -> str:
        """Generate a response."""
        system = f"You are {self.name}, {self.role}."
        
        messages = [{"role": "system", "content": system}]
        messages.extend(self.history[-4:])  # Last 2 exchanges
        messages.append({"role": "user", "content": message})
        
        response = self.client.chat(messages)
        
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": response})
        
        return response
```

### Step 2: Create a Team

```python
client = KimiClient(base_url="http://localhost:8000")

# Create agents
pm = Agent("Alice", "a product manager focused on user needs", client)
dev = Agent("Bob", "a senior software engineer", client)
designer = Agent("Carol", "a UX designer", client)
```

### Step 3: Facilitate Discussion

```python
def team_discussion(topic: str, agents: List[Agent], rounds: int = 2):
    """Facilitate a team discussion."""
    print(f"=== Team Discussion: {topic} ===\n")
    
    for round_num in range(rounds):
        print(f"--- Round {round_num + 1} ---\n")
        
        for agent in agents:
            if round_num == 0:
                prompt = f"Discuss: {topic}"
            else:
                # Build context from other agents
                context = "\n".join([
                    f"{a.name}: {a.history[-1]['content'][:100]}..."
                    for a in agents if a != agent and a.history
                ])
                prompt = f"Given these views:\n{context}\n\nYour perspective on: {topic}"
            
            response = agent.respond(prompt)
            print(f"{agent.name}: {response}\n")
        
        print()

# Run discussion
team_discussion(
    "Design a feature to help remote teams collaborate better",
    [pm, dev, designer],
    rounds=2
)
```

---

## Tutorial 5: Performance Benchmarking

Benchmark your Kimi-K2 deployment.

### Step 1: Basic Latency Test

```python
from kimi_k2.client import KimiClient
from kimi_k2.benchmark.runner import BenchmarkRunner

client = KimiClient(base_url="http://localhost:8000")
runner = BenchmarkRunner(client)

# Define test prompts
prompts = [
    "What is 2+2?",
    "Explain machine learning briefly.",
    "Write a Python hello world function."
]

# Run benchmark
stats = runner.run_latency_test(prompts, num_runs=5)

print("=== Latency Benchmark Results ===")
for key, value in stats.items():
    print(f"{key}: {value:.2f}")
```

### Step 2: Throughput Test

```python
# Test throughput
prompts = ["Short prompt", "Another short prompt"]
throughput_stats = runner.run_throughput_test(prompts, duration_seconds=30)

print("\n=== Throughput Benchmark Results ===")
print(f"Requests per second: {throughput_stats['requests_per_second']:.2f}")
print(f"Tokens per second: {throughput_stats['tokens_per_second']:.2f}")
```

### Step 3: Export Results

```python
# Export detailed results
runner.export_results("benchmark_results.json")
print("\nResults exported to benchmark_results.json")
```

### Step 4: Command Line Benchmarking

```bash
# Run from command line
kimi-benchmark \
  --url http://localhost:8000 \
  --prompts "Test 1" "Test 2" "Test 3" \
  --runs 10 \
  --output results.json
```

---

## Next Steps

- Explore the [API Reference](api_reference.md) for detailed documentation
- Read the [Advanced Usage Guide](advanced_usage.md) for more patterns
- Check out the example code in `src/kimi_k2/examples/`
- Review [deployment options](deploy_guidance.md) for production use

## Troubleshooting

### Connection Issues

If you can't connect to the service:

```python
# Test connection
import requests
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Service is running: {response.status_code}")
except requests.ConnectionError:
    print("Cannot connect to service. Check if it's running.")
```

### Performance Issues

If responses are slow:
1. Check your deployment configuration
2. Monitor GPU utilization
3. Adjust batch sizes
4. Consider using multiple workers

### Memory Issues

If you encounter OOM errors:
1. Reduce `max_tokens`
2. Limit conversation history
3. Use smaller batch sizes
4. Check deployment memory settings

## Community and Support

- [GitHub Issues](https://github.com/moonshotai/Kimi-K2/issues)
- [Discord](https://discord.gg/TYU2fdJykW)
- Email: support@moonshot.cn
