# Kimi K2 Quick Tutorial

This tutorial will walk you through common use cases for Kimi K2.

## Table of Contents

1. [Basic Chat](#basic-chat)
2. [Tool Calling](#tool-calling)
3. [Using Plugins](#using-plugins)
4. [Memory Management](#memory-management)
5. [Running Benchmarks](#running-benchmarks)

## Basic Chat

### Simple Conversation

```python
from openai import OpenAI

# Initialize client
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

# Send a message
response = client.chat.completions.create(
    model="kimi-k2",
    messages=[
        {"role": "system", "content": "You are Kimi, an AI assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    temperature=0.6,
    max_tokens=500
)

print(response.choices[0].message.content)
```

### Streaming Responses

```python
# Stream the response
response = client.chat.completions.create(
    model="kimi-k2",
    messages=[{"role": "user", "content": "Tell me a story."}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='', flush=True)
```

## Tool Calling

### Weather Tool Example

```python
import json

# Define a weather tool
def get_weather(city: str) -> dict:
    """Get weather for a city (mock implementation)."""
    return {
        "city": city,
        "temperature": "22°C",
        "condition": "Sunny"
    }

# Tool schema
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
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

# Tool mapping
tool_map = {"get_weather": get_weather}

# Use tools in conversation
messages = [
    {"role": "user", "content": "What's the weather in Tokyo?"}
]

while True:
    response = client.chat.completions.create(
        model="kimi-k2",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    choice = response.choices[0]
    
    if choice.finish_reason == "tool_calls":
        # Add assistant message with tool calls
        messages.append(choice.message)
        
        # Execute tool calls
        for tool_call in choice.message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            # Call the function
            result = tool_map[func_name](**func_args)
            
            # Add tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": func_name,
                "content": json.dumps(result)
            })
    else:
        # Final response
        print(choice.message.content)
        break
```

## Using Plugins

### Loading a Plugin

```python
from plugins.core.loader import PluginLoader

# Initialize plugin loader
loader = PluginLoader()

# List available plugins
plugins = loader.list_plugins()
print("Available plugins:", plugins)

# Load a plugin
example_plugin = loader.load_plugin("example_tool")

# Use the plugin
result = example_plugin.execute("Hello, world!")
print("Plugin result:", result)
```

### Creating a Custom Plugin

1. Create plugin directory:
```bash
mkdir -p plugins/examples/my_plugin
```

2. Create `__init__.py`:
```python
from plugins.core.loader import Plugin

class MyPlugin(Plugin):
    def initialize(self):
        print(f"Initializing {self.name}")
        return True
    
    def execute(self, input_data):
        # Your plugin logic here
        return {"processed": input_data.upper()}
```

3. Register in `plugins/core/registry.json`:
```json
{
  "my_plugin": {
    "name": "my_plugin",
    "version": "1.0.0",
    "description": "My custom plugin",
    "type": "tool",
    "path": "examples/my_plugin",
    "class": "MyPlugin"
  }
}
```

4. Test your plugin:
```bash
python plugins/core/interactive_test.py --plugin my_plugin
```

## Memory Management

### Storing Conversations

```python
from memory.storage.manager import MemoryManager

# Initialize memory manager
memory = MemoryManager(backend='file')

# Store a message
memory.store_message(
    user_id="user123",
    role="user",
    content="What is machine learning?"
)

memory.store_message(
    user_id="user123",
    role="assistant",
    content="Machine learning is a subset of AI..."
)

# Retrieve history
history = memory.get_history(user_id="user123", limit=10)
print("Conversation history:", history)
```

### User Profiles and Personalization

```python
# Update user profile
memory.update_profile(
    user_id="user123",
    profile_updates={
        'preferences': {
            'language': 'en',
            'expertise_level': 'expert',
            'interests': ['AI', 'ML', 'Python']
        }
    }
)

# Get personalized context
context = memory.get_personalized_context(user_id="user123")
print("Personalization hints:", context['personalization_hints'])
```

## Running Benchmarks

### Execute a Benchmark

```python
from benchmarks.tools.run_benchmark import BenchmarkRunner

# Initialize runner
runner = BenchmarkRunner()

# Run a benchmark
results = runner.run_benchmark(
    dataset="livecodebench",
    model_path="./models/Kimi-K2-Instruct",
    output_dir="./results"
)

print("Benchmark results:", results['metrics'])
```

### View Metrics in Grafana

```bash
# Start monitoring stack
cd benchmarks/dashboards
docker-compose up -d

# Access Grafana at http://localhost:3000
# Default credentials: admin/kimi-k2-admin
```

## Advanced Topics

### Multi-pass Fine-tuning

```python
from training.pipelines.multipass import MultiPassTrainer

# Initialize trainer
trainer = MultiPassTrainer(
    base_model="Kimi-K2-Base",
    output_dir="./models/finetuned"
)

# Define training passes
passes = [
    {
        "name": "general",
        "data": "data/general_qa.jsonl",
        "epochs": 3,
        "learning_rate": 2e-5
    },
    {
        "name": "coding",
        "data": "data/coding_tasks.jsonl",
        "epochs": 2,
        "learning_rate": 1e-5
    }
]

# Run training
final_model = trainer.train(passes)
```

### Data Augmentation

```python
from training.augmentation.augmentor import DataAugmentor

# Initialize augmentor
augmentor = DataAugmentor()

# Augment data
original_data = [
    {"input": "What is AI?", "output": "AI is..."}
]

augmented = augmentor.augment(
    data=original_data,
    techniques=['paraphrase', 'noise_injection'],
    augmentation_factor=3
)

# Save augmented data
augmentor.save_augmented_data(augmented, 'augmented.jsonl')
```

## Tips and Best Practices

1. **Temperature Settings**: Use 0.6 for balanced responses, lower for more deterministic output
2. **Context Management**: Keep conversations focused; use memory management for long contexts
3. **Tool Calling**: Provide clear, detailed tool descriptions for best results
4. **Plugin Development**: Follow the development guide and test thoroughly
5. **Monitoring**: Enable monitoring in production for performance insights

## Next Steps

- [Explore more examples](../community/tutorials/)
- [Read the full documentation](https://moonshotai.github.io/Kimi-K2/)
- [Join the community](https://discord.gg/TYU2fdJykW)
- [Contribute](../CONTRIBUTING.md)

## Troubleshooting

### Common Issues

**Q: Model loading is slow**
A: Ensure model files are on SSD storage and use adequate GPU memory

**Q: Tool calls not working**
A: Check that `--enable-auto-tool-choice` and `--tool-call-parser kimi_k2` are set

**Q: Out of memory errors**
A: Reduce batch size or increase tensor parallelism

For more help:
- Check the [documentation](../docs/)
- Ask in [Discord](https://discord.gg/TYU2fdJykW)
- Email [support@moonshot.cn](mailto:support@moonshot.cn)
