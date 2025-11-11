# Getting Started with Kimi K2

Welcome to Kimi K2! This guide will help you get started with deploying and using Kimi K2.

## Quick Links

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-compatible GPU (for optimal performance)
- 16GB+ RAM recommended
- Docker (optional, for containerized deployment)

### Step 1: Clone the Repository

```bash
git clone https://github.com/moonshotai/Kimi-K2.git
cd Kimi-K2
```

### Step 2: Run Setup Wizard

We provide an interactive setup wizard to help you configure Kimi K2:

```bash
python community/wizards/setup_wizard.py
```

The wizard will guide you through:
- Choosing deployment type
- Configuring storage
- Setting up plugins
- Configuring memory management
- Setting up monitoring

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install benchmark dependencies (optional)
pip install -r benchmarks/requirements.txt
```

### Step 4: Download Model

Download the Kimi K2 model from [Hugging Face](https://huggingface.co/moonshotai/Kimi-K2-Instruct):

```bash
# Using huggingface-cli
huggingface-cli download moonshotai/Kimi-K2-Instruct --local-dir ./models/Kimi-K2-Instruct

# Or using git-lfs
git lfs install
git clone https://huggingface.co/moonshotai/Kimi-K2-Instruct ./models/Kimi-K2-Instruct
```

## Basic Usage

### Starting the Server

#### Using vLLM

```bash
vllm serve ./models/Kimi-K2-Instruct \
  --port 8000 \
  --served-model-name kimi-k2 \
  --trust-remote-code \
  --tensor-parallel-size 16 \
  --enable-auto-tool-choice \
  --tool-call-parser kimi_k2
```

#### Using SGLang

```bash
python -m sglang.launch_server \
  --model-path ./models/Kimi-K2-Instruct \
  --tp 16 \
  --trust-remote-code \
  --tool-call-parser kimi_k2
```

For detailed deployment options, see [Deployment Guide](deploy_guidance.md).

### Making Your First Request

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="kimi-k2",
    messages=[
        {"role": "system", "content": "You are Kimi, an AI assistant created by Moonshot AI."},
        {"role": "user", "content": "Hello! Tell me about yourself."}
    ],
    temperature=0.6,
    max_tokens=256
)

print(response.choices[0].message.content)
```

## Configuration

### Basic Configuration

Create a configuration file `config/kimi_k2_config.json`:

```json
{
  "deployment_type": "local",
  "storage_backend": "file",
  "storage_path": "./data",
  "plugins_enabled": true,
  "memory_enabled": true,
  "max_history": 1000,
  "enable_personalization": true
}
```

### Advanced Configuration

For production deployments:

```yaml
# config/production.yaml
deployment:
  type: production
  replicas: 4
  
model:
  path: /models/Kimi-K2-Instruct
  tensor_parallel_size: 16
  max_batch_size: 128
  
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  
monitoring:
  enabled: true
  prometheus_port: 9090
  grafana_enabled: true
```

## Examples

### Chat Completion

```python
def simple_chat():
    messages = [
        {"role": "system", "content": "You are Kimi, an AI assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    response = client.chat.completions.create(
        model="kimi-k2",
        messages=messages,
        temperature=0.6
    )
    
    return response.choices[0].message.content
```

### Tool Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather information",
        "parameters": {
            "type": "object",
            "required": ["city"],
            "properties": {
                "city": {"type": "string", "description": "City name"}
            }
        }
    }
}]

response = client.chat.completions.create(
    model="kimi-k2",
    messages=[{"role": "user", "content": "What's the weather in Beijing?"}],
    tools=tools,
    tool_choice="auto"
)
```

For more examples, see [Tool Calling Guide](tool_call_guidance.md).

### Using Plugins

```python
from plugins.core.loader import PluginLoader

# Load a plugin
loader = PluginLoader()
weather_plugin = loader.load_plugin("weather_api")

# Use the plugin
result = weather_plugin.execute(city="Beijing")
print(result)
```

## Troubleshooting

### Common Issues

#### Model Loading Fails

**Problem**: Out of memory error when loading model

**Solution**: 
- Ensure you have sufficient GPU memory
- Increase tensor parallelism: `--tensor-parallel-size 16`
- Reduce batch size: `--max-num-batched-tokens 8192`

#### Slow Inference

**Problem**: Token generation is slow

**Solution**:
- Enable CUDA graphs
- Use optimal batch size
- Check GPU utilization
- Consider using expert parallelism

#### Tool Calls Not Working

**Problem**: Tool calls are not being recognized

**Solution**:
- Ensure `--enable-auto-tool-choice` is set
- Verify `--tool-call-parser kimi_k2` is configured
- Check tool schema format

### Getting Help

- **Documentation**: See [docs/](.)
- **Issues**: Open an issue on [GitHub](https://github.com/moonshotai/Kimi-K2/issues)
- **Discord**: Join our [Discord community](https://discord.gg/TYU2fdJykW)
- **Email**: Contact [support@moonshot.cn](mailto:support@moonshot.cn)

## Next Steps

- [Explore Benchmarks](../benchmarks/README.md)
- [Create Plugins](../plugins/README.md)
- [Configure Memory Management](../memory/README.md)
- [Set Up Monitoring](../monitoring/README.md)
- [Training Enhancements](../training/README.md)

## Additional Resources

- [Technical Report](https://www.arxiv.org/abs/2507.20534)
- [Tech Blog](https://moonshotai.github.io/Kimi-K2/)
- [Model Card](https://huggingface.co/moonshotai/Kimi-K2-Instruct)
- [API Documentation](https://platform.moonshot.ai)

---

**Welcome to the Kimi K2 community!** We're excited to see what you build.
