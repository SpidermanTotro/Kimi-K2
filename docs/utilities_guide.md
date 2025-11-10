# Kimi-K2 Utilities and Examples

This repository now includes comprehensive utilities, examples, and tools to help you get the most out of Kimi-K2.

## 🚀 Quick Start

### Installation

```bash
# Install the utilities package
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Basic Usage

```python
from kimi_k2.client import KimiClient

# Initialize client
client = KimiClient(
    base_url="http://localhost:8000",
    temperature=0.6
)

# Simple chat
response = client.simple_chat("What is Kimi K2?")
print(response)
```

### Command Line Interface

```bash
# Interactive chat
kimi-cli interactive --url http://localhost:8000

# Single message
kimi-cli chat --url http://localhost:8000 "Write a Python function"

# With streaming
kimi-cli chat --url http://localhost:8000 --stream "Tell me a story"
```

## 📚 Features

### Enhanced Client (`kimi_k2.client.KimiClient`)

- **Simple API**: Easy-to-use Python client for Kimi-K2
- **Streaming Support**: Stream responses for better UX
- **Tool Calling**: Automatic tool call handling
- **Flexible Configuration**: Customize temperature, max tokens, etc.

```python
from kimi_k2.client import KimiClient

client = KimiClient(base_url="http://localhost:8000")

# Streaming chat
for chunk in client.chat(messages, stream=True):
    print(chunk, end="", flush=True)

# Tool calling
response = client.chat_with_tools(
    messages=messages,
    tools=tool_schemas,
    tool_map=tool_functions
)
```

### Tool Management (`kimi_k2.tools.ToolManager`)

- **Automatic Schema Generation**: Generate OpenAI-compatible schemas from Python functions
- **Type Inference**: Automatic parameter type detection
- **Easy Registration**: Simple decorator-based tool registration

```python
from kimi_k2.tools import ToolManager

tm = ToolManager()

@tm.register(description="Get weather information")
def get_weather(city: str) -> dict:
    return {"weather": "Sunny", "city": city}

# Use with client
client.chat_with_tools(
    messages=messages,
    tools=tm.get_tool_schemas(),
    tool_map=tm.get_tool_map()
)
```

### Command Line Interface

Powerful CLI for interacting with Kimi-K2:

```bash
# Interactive mode
kimi-cli interactive --url http://localhost:8000

# Single message
kimi-cli chat --url http://localhost:8000 "Your question here"

# Custom temperature
kimi-cli chat --url http://localhost:8000 --temperature 0.8 "Be creative"

# From stdin
echo "What is AI?" | kimi-cli chat --url http://localhost:8000
```

### Benchmarking Tools

Comprehensive performance testing:

```python
from kimi_k2.benchmark.runner import BenchmarkRunner

runner = BenchmarkRunner(client)

# Latency test
stats = runner.run_latency_test(prompts, num_runs=5)
print(f"Mean latency: {stats['mean_latency_ms']:.2f}ms")

# Throughput test
stats = runner.run_throughput_test(prompts, duration_seconds=60)
print(f"Throughput: {stats['requests_per_second']:.2f} req/s")
```

Or use the CLI:

```bash
kimi-benchmark --url http://localhost:8000 \
  --prompts "Test 1" "Test 2" \
  --runs 10 \
  --output results.json
```

## 📖 Examples

### Basic Chat

```python
from kimi_k2.client import KimiClient

client = KimiClient(base_url="http://localhost:8000")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain quantum computing."}
]

response = client.chat(messages)
print(response)
```

### Tool Calling

```python
from kimi_k2.client import KimiClient
from kimi_k2.tools import ToolManager

client = KimiClient(base_url="http://localhost:8000")
tm = ToolManager()

@tm.register(description="Calculate mathematical expressions")
def calculate(expression: str) -> dict:
    try:
        result = eval(expression, {"__builtins__": {}})
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

messages = [
    {"role": "user", "content": "What is 15 * 23? Use the calculator tool."}
]

response = client.chat_with_tools(
    messages=messages,
    tools=tm.get_tool_schemas(),
    tool_map=tm.get_tool_map()
)
print(response)
```

### Multi-Agent System

```python
from kimi_k2.client import KimiClient

class Agent:
    def __init__(self, name, role, client):
        self.name = name
        self.role = role
        self.client = client
    
    def respond(self, message):
        system = f"You are {self.name}, {self.role}."
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": message}
        ]
        return self.client.chat(messages)

client = KimiClient(base_url="http://localhost:8000")

pm = Agent("Alice", "product manager", client)
engineer = Agent("Bob", "software engineer", client)
designer = Agent("Carol", "UX designer", client)

# Simulate team discussion
task = "Design a feature for mobile app"
print(f"PM: {pm.respond(task)}")
print(f"Engineer: {engineer.respond(task)}")
print(f"Designer: {designer.respond(task)}")
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=kimi_k2 --cov-report=html

# Run specific tests
pytest tests/test_client.py -v
```

## 📚 Documentation

- **[Tutorials](docs/tutorials.md)**: Step-by-step guides for common tasks
- **[API Reference](docs/api_reference.md)**: Complete API documentation
- **[Advanced Usage](docs/advanced_usage.md)**: Advanced patterns and best practices
- **[Deployment Guide](docs/deploy_guidance.md)**: Deployment instructions
- **[Tool Calling Guide](docs/tool_call_guidance.md)**: Tool calling examples

## 📦 Package Structure

```
Kimi-K2/
├── src/kimi_k2/
│   ├── client.py           # Enhanced Kimi-K2 client
│   ├── tools.py            # Tool management utilities
│   ├── cli/
│   │   └── main.py         # Command line interface
│   ├── benchmark/
│   │   └── runner.py       # Performance benchmarking
│   └── examples/
│       ├── basic_chat.py   # Basic chat examples
│       ├── tool_calling.py # Tool calling examples
│       ├── code_assistant.py # Code generation
│       └── multi_agent.py  # Multi-agent systems
├── tests/                  # Test suite
├── docs/                   # Documentation
└── setup.py               # Package configuration
```

## 🎯 Example Use Cases

### 1. Code Generation Assistant

```python
from kimi_k2.client import KimiClient

client = KimiClient(base_url="http://localhost:8000")

code = client.simple_chat(
    "Write a Python function to implement binary search",
    system_message="You are an expert Python developer"
)
```

### 2. Research Assistant with Tools

```python
from kimi_k2.tools import ToolManager

tm = ToolManager()

@tm.register(description="Search academic papers")
def search_papers(query: str) -> dict:
    # Implementation here
    pass

@tm.register(description="Summarize paper")
def summarize(paper_id: str) -> dict:
    # Implementation here
    pass

# Use tools for research
response = client.chat_with_tools(
    messages=[{"role": "user", "content": "Research recent advances in transformers"}],
    tools=tm.get_tool_schemas(),
    tool_map=tm.get_tool_map()
)
```

### 3. Interactive Storytelling

```python
narrator = Agent("Narrator", "storyteller", client)
character1 = Agent("Hero", "brave adventurer", client)
character2 = Agent("Wizard", "wise mage", client)

# Collaborative story creation
scene = narrator.respond("Start a fantasy adventure story")
action1 = character1.respond(f"In this scene: {scene}. What do you do?")
action2 = character2.respond(f"After {action1}, what happens?")
```

## 🔧 Configuration

### Environment Variables

```bash
export KIMI_BASE_URL="http://localhost:8000"
export KIMI_API_KEY="your-api-key"
export KIMI_MODEL="kimi-k2"
```

### Python Configuration

```python
client = KimiClient(
    base_url="http://localhost:8000",
    api_key="your-api-key",
    model_name="kimi-k2",
    temperature=0.6,  # Recommended
    max_tokens=2048
)
```

## 🐛 Troubleshooting

### Connection Issues

```python
# Test connection
import requests
response = requests.get("http://localhost:8000/health")
print(f"Status: {response.status_code}")
```

### Performance Optimization

- Use streaming for long responses
- Implement caching for repeated queries
- Batch process multiple requests
- Monitor token usage

## 🤝 Contributing

We welcome contributions! See our examples and utilities as a starting point.

## 📄 License

Both the code and model weights are released under the [Modified MIT License](LICENSE).

## 🔗 Resources

- **Model Weights**: [Hugging Face](https://huggingface.co/moonshotai/Kimi-K2-Instruct)
- **Technical Report**: [arXiv](https://www.arxiv.org/abs/2507.20534)
- **API Access**: [Moonshot AI Platform](https://platform.moonshot.ai)
- **Community**: [Discord](https://discord.gg/TYU2fdJykW)

## 📞 Support

- Email: support@moonshot.cn
- GitHub Issues: [Report Issues](https://github.com/moonshotai/Kimi-K2/issues)
- Discord: [Join Community](https://discord.gg/TYU2fdJykW)
