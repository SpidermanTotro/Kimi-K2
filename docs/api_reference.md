# API Reference

Complete API reference for Kimi-K2 utilities and examples.

## Table of Contents

- [KimiClient](#kimiclient)
- [ToolManager](#toolmanager)
- [Command Line Interface](#command-line-interface)
- [Benchmark Runner](#benchmark-runner)

---

## KimiClient

Enhanced client for interacting with Kimi-K2 models.

### Constructor

```python
KimiClient(
    base_url: str,
    api_key: str = "dummy",
    model_name: str = "kimi-k2",
    temperature: float = 0.6,
    max_tokens: int = 2048
)
```

**Parameters:**
- `base_url` (str): Base URL of the Kimi-K2 service (e.g., "http://localhost:8000")
- `api_key` (str): API key for authentication (default: "dummy" for local deployments)
- `model_name` (str): Name of the model to use (default: "kimi-k2")
- `temperature` (float): Sampling temperature, recommended: 0.6 (default: 0.6)
- `max_tokens` (int): Maximum tokens to generate (default: 2048)

**Example:**
```python
from kimi_k2.client import KimiClient

client = KimiClient(
    base_url="http://localhost:8000",
    temperature=0.6
)
```

### Methods

#### chat()

Send a chat completion request.

```python
chat(
    messages: List[Dict[str, str]],
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, Iterator[str]]
```

**Parameters:**
- `messages`: List of message dictionaries with 'role' and 'content' keys
- `temperature`: Override default temperature (optional)
- `max_tokens`: Override default max_tokens (optional)
- `stream`: Whether to stream the response (default: False)
- `**kwargs`: Additional parameters to pass to the API

**Returns:**
- `str`: Response content (if stream=False)
- `Iterator[str]`: Iterator of response chunks (if stream=True)

**Example:**
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is Python?"}
]
response = client.chat(messages)
```

#### simple_chat()

Simple one-turn chat.

```python
simple_chat(
    user_message: str,
    system_message: Optional[str] = None
) -> str
```

**Parameters:**
- `user_message`: User's message
- `system_message`: Optional system message

**Returns:**
- `str`: Model's response

**Example:**
```python
response = client.simple_chat(
    "Explain quantum computing",
    system_message="You are a physics professor"
)
```

#### chat_with_tools()

Chat with automatic tool calling.

```python
chat_with_tools(
    messages: List[Dict[str, str]],
    tools: List[Dict[str, Any]],
    tool_map: Dict[str, callable],
    max_iterations: int = 10,
    temperature: Optional[float] = None,
    **kwargs
) -> str
```

**Parameters:**
- `messages`: List of message dictionaries
- `tools`: List of tool definitions in OpenAI format
- `tool_map`: Dictionary mapping tool names to callable functions
- `max_iterations`: Maximum number of tool call iterations (default: 10)
- `temperature`: Override default temperature (optional)
- `**kwargs`: Additional parameters

**Returns:**
- `str`: Final response content

**Example:**
```python
def get_weather(city: str) -> dict:
    return {"weather": "Sunny"}

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
            "type": "object",
            "required": ["city"],
            "properties": {
                "city": {"type": "string"}
            }
        }
    }
}]

tool_map = {"get_weather": get_weather}

response = client.chat_with_tools(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_map=tool_map
)
```

---

## ToolManager

Manage tools for Kimi-K2 function calling.

### Constructor

```python
ToolManager()
```

**Example:**
```python
from kimi_k2.tools import ToolManager

tool_manager = ToolManager()
```

### Methods

#### register()

Decorator to register a function as a tool.

```python
@register(
    name: Optional[str] = None,
    description: Optional[str] = None
)
```

**Parameters:**
- `name`: Optional custom name for the tool (default: function name)
- `description`: Description of the tool (default: function docstring)

**Returns:**
- Decorator function

**Example:**
```python
@tool_manager.register(description="Calculate sum of two numbers")
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

#### get_tool_schemas()

Get all registered tool schemas.

```python
get_tool_schemas() -> List[Dict[str, Any]]
```

**Returns:**
- `List[Dict]`: List of tool schemas in OpenAI format

**Example:**
```python
schemas = tool_manager.get_tool_schemas()
```

#### get_tool_map()

Get mapping of tool names to functions.

```python
get_tool_map() -> Dict[str, Callable]
```

**Returns:**
- `Dict[str, Callable]`: Dictionary of tool names to callable functions

**Example:**
```python
tool_map = tool_manager.get_tool_map()
```

#### call_tool()

Call a registered tool by name.

```python
call_tool(name: str, **kwargs) -> Any
```

**Parameters:**
- `name`: Tool name
- `**kwargs`: Arguments to pass to the tool

**Returns:**
- Tool result

**Raises:**
- `KeyError`: If tool not found

**Example:**
```python
result = tool_manager.call_tool("add", a=5, b=3)
# result: 8
```

---

## Command Line Interface

### kimi-cli chat

Send a chat message to Kimi-K2.

```bash
kimi-cli chat [OPTIONS] [MESSAGE]
```

**Options:**
- `--url TEXT`: Base URL of Kimi-K2 service (required)
- `--model TEXT`: Model name (default: "kimi-k2")
- `--api-key TEXT`: API key (default: "dummy")
- `--system TEXT`: System message
- `--temperature FLOAT`: Temperature (default: 0.6)
- `--max-tokens INTEGER`: Max tokens (default: 2048)
- `--stream/--no-stream`: Stream output (default: False)

**Examples:**
```bash
# Basic chat
kimi-cli chat --url http://localhost:8000 "What is AI?"

# With system message
kimi-cli chat --url http://localhost:8000 \
  --system "You are a poet" \
  "Write a haiku about coding"

# Streaming
kimi-cli chat --url http://localhost:8000 --stream "Tell me a story"

# From stdin
echo "What is Python?" | kimi-cli chat --url http://localhost:8000
```

### kimi-cli interactive

Start an interactive chat session.

```bash
kimi-cli interactive [OPTIONS]
```

**Options:**
- `--url TEXT`: Base URL of Kimi-K2 service (required)
- `--model TEXT`: Model name (default: "kimi-k2")
- `--api-key TEXT`: API key (default: "dummy")
- `--temperature FLOAT`: Temperature (default: 0.6)

**Commands in interactive mode:**
- `/quit` - Exit the chat
- `/clear` - Clear chat history
- `/help` - Show help

**Example:**
```bash
kimi-cli interactive --url http://localhost:8000
```

---

## Benchmark Runner

Run benchmarks on Kimi-K2 models.

### Constructor

```python
BenchmarkRunner(client: KimiClient)
```

**Parameters:**
- `client`: KimiClient instance to benchmark

**Example:**
```python
from kimi_k2.client import KimiClient
from kimi_k2.benchmark.runner import BenchmarkRunner

client = KimiClient(base_url="http://localhost:8000")
runner = BenchmarkRunner(client)
```

### Methods

#### run_latency_test()

Run latency benchmarks.

```python
run_latency_test(
    prompts: List[str],
    num_runs: int = 3,
    warmup: bool = True
) -> Dict[str, Any]
```

**Parameters:**
- `prompts`: List of prompts to test
- `num_runs`: Number of runs per prompt (default: 3)
- `warmup`: Whether to do a warmup run (default: True)

**Returns:**
- `Dict`: Dictionary with benchmark statistics:
  - `num_tests`: Total number of tests run
  - `mean_latency_ms`: Mean latency in milliseconds
  - `median_latency_ms`: Median latency
  - `min_latency_ms`: Minimum latency
  - `max_latency_ms`: Maximum latency
  - `stdev_latency_ms`: Standard deviation

**Example:**
```python
prompts = [
    "What is AI?",
    "Explain quantum computing",
    "Write a Python function"
]
stats = runner.run_latency_test(prompts, num_runs=5)
print(f"Mean latency: {stats['mean_latency_ms']:.2f}ms")
```

#### run_throughput_test()

Run throughput benchmark.

```python
run_throughput_test(
    prompts: List[str],
    duration_seconds: int = 60
) -> Dict[str, Any]
```

**Parameters:**
- `prompts`: List of prompts to cycle through
- `duration_seconds`: How long to run the test (default: 60)

**Returns:**
- `Dict`: Dictionary with throughput statistics:
  - `duration_seconds`: Actual test duration
  - `total_requests`: Total requests completed
  - `total_tokens`: Total tokens generated (estimated)
  - `requests_per_second`: Requests per second
  - `tokens_per_second`: Tokens per second

**Example:**
```python
prompts = ["Short prompt", "Another prompt"]
stats = runner.run_throughput_test(prompts, duration_seconds=30)
print(f"Throughput: {stats['requests_per_second']:.2f} req/s")
```

#### export_results()

Export results to JSON file.

```python
export_results(filepath: str) -> None
```

**Parameters:**
- `filepath`: Path to save results

**Example:**
```python
runner.export_results("benchmark_results.json")
```

### Command Line Usage

```bash
kimi-benchmark [OPTIONS]
```

**Options:**
- `--url TEXT`: Base URL of service (required)
- `--model TEXT`: Model name (default: "kimi-k2")
- `--prompts TEXT [TEXT ...]`: Test prompts
- `--runs INTEGER`: Runs per prompt (default: 3)
- `--output TEXT`: Output file for results

**Example:**
```bash
kimi-benchmark --url http://localhost:8000 \
  --prompts "Test 1" "Test 2" "Test 3" \
  --runs 5 \
  --output results.json
```

---

## Type Definitions

### Message Format

Messages follow the OpenAI chat format:

```python
{
    "role": str,  # "system", "user", "assistant", or "tool"
    "content": str,  # Message content
    # For tool responses:
    "tool_call_id": str,  # (optional)
    "name": str,  # (optional) Tool name
}
```

### Tool Schema Format

Tools follow the OpenAI function calling format:

```python
{
    "type": "function",
    "function": {
        "name": str,
        "description": str,
        "parameters": {
            "type": "object",
            "required": List[str],
            "properties": {
                "param_name": {
                    "type": str,  # "string", "integer", "number", "boolean", "array", "object"
                    "description": str,
                    # Additional fields like "enum", "items", etc.
                }
            }
        }
    }
}
```
