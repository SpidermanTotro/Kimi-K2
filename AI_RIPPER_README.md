# AI Ripper - Model Extraction & Analysis Tool

## Overview

AI Ripper is a powerful tool for extracting, analyzing, and exporting AI models from endpoints. It provides both a graphical user interface (GUI) and command-line interface (CLI) for maximum flexibility.

## Features

### Core Functionality
- **Endpoint Scanning**: Probe and extract information from AI model endpoints
- **Multi-endpoint Support**: Scan and compare multiple endpoints simultaneously
- **Export Formats**: Support for JSON, Python, GGUF, and ONNX formats
- **Metadata Extraction**: Extract comprehensive model metadata including architecture, capabilities, and parameters

### Visual Interface (GUI)
- **Cross-platform GUI**: Built with Tkinter for Windows, macOS, and Linux
- **Intuitive Controls**: Easy-to-use interface with drag-and-drop simplicity
- **Real-time Progress**: Live progress indicators and status updates
- **Visualization Tools**:
  - Token attention heatmaps
  - Response time graphs
  - Behavior classification metrics
  - Multi-endpoint comparison charts

### Advanced Features
- **Adaptive Memory Management**: Handles large models on low-resource systems
- **Security & Ethics**: Built-in consent prompts and security checks
- **Settings Configuration**: Advanced options for timeout, retries, and scan depth
- **Detailed Logging**: Comprehensive logs viewer for debugging and analysis

## Installation

### Requirements

```bash
# Install dependencies
pip install -r requirements.txt
```

Required packages:
- `requests>=2.31.0` - HTTP client for endpoint communication
- `matplotlib>=3.7.0` - Visualization and plotting
- `numpy>=1.24.0` - Numerical computing
- `Flask>=2.3.0` - Optional, for web interface
- `Flask-CORS>=4.0.0` - Optional, for CORS support

### Quick Start

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python ai_ripper_gui.py

# Or use the CLI
python ai_ripper_cli.py --help
```

## Usage

### GUI Interface

Launch the graphical interface:

```bash
python ai_ripper_gui.py
```

#### GUI Workflow:

1. **Add Endpoints**:
   - Enter the endpoint URL (e.g., `http://localhost:8000`)
   - Optionally provide an API key
   - Give the endpoint a name
   - Click "Add Endpoint"

2. **Configure Settings** (Settings Tab):
   - Set timeout duration
   - Configure max retries
   - Adjust scan depth
   - Enable adaptive memory management

3. **Start Ripping**:
   - Select export format (JSON, Python, GGUF, ONNX)
   - Click "🚀 Start Ripping"
   - Monitor progress in real-time

4. **View Results**:
   - Switch to "Visualization" tab to see graphs
   - Compare multiple endpoints
   - Export selected models

5. **Export**:
   - Select an endpoint from the list
   - Choose export format
   - Click "💾 Export Selected"
   - Choose save location

### CLI Interface

The CLI provides powerful command-line access to all features.

#### Basic Commands:

```bash
# Rip a single endpoint
python ai_ripper_cli.py rip http://localhost:8000 -o model.json

# Rip with API key and custom settings
python ai_ripper_cli.py rip http://api.example.com \
  --api-key YOUR_API_KEY \
  --depth 5 \
  --timeout 60 \
  -o model.py \
  -f python

# Compare multiple endpoints
python ai_ripper_cli.py compare \
  http://endpoint1.com \
  http://endpoint2.com \
  http://endpoint3.com \
  -o comparison.json

# List available export formats
python ai_ripper_cli.py list-formats
```

#### CLI Options:

**Rip Command:**
- `-k, --api-key`: API key for authentication
- `-o, --output`: Output file path
- `-f, --format`: Export format (json, python, gguf, onnx)
- `-t, --timeout`: Request timeout in seconds (default: 30)
- `-r, --retries`: Maximum retries (default: 3)
- `-d, --depth`: Scan depth (default: 3)
- `--no-consent`: Skip ethical consent prompt

**Compare Command:**
- `-o, --output`: Output file for comparison results
- `-t, --timeout`: Request timeout in seconds
- `-r, --retries`: Maximum retries
- `-d, --depth`: Scan depth
- `--no-consent`: Skip ethical consent prompt

### Python API

You can also use AI Ripper programmatically:

```python
from ai_ripper_core import AIRipper, EndpointConfig

# Create ripper instance
ripper = AIRipper()

# Configure endpoint
config = EndpointConfig(
    url="http://localhost:8000",
    api_key="your-api-key",  # Optional
    timeout=30,
    max_retries=3,
    scan_depth=3
)

# Add endpoint
ripper.add_endpoint("my_model", config)

# Set progress callback (optional)
def on_progress(progress):
    print(f"Progress: {progress.progress_percentage:.1f}%")
    print(f"Task: {progress.current_task}")

ripper.set_progress_callback(on_progress)

# Rip the endpoint
success = ripper.rip_endpoint("my_model")

if success:
    # Export to different formats
    ripper.export_to_json("my_model", "model.json")
    ripper.export_to_python("my_model", "model_config.py")
    ripper.export_to_gguf("my_model", "model.gguf")
    
    # Get metadata
    metadata = ripper.extracted_models["my_model"]
    print(f"Model: {metadata.name}")
    print(f"Capabilities: {metadata.capabilities}")

# Compare multiple endpoints
endpoint_names = ["endpoint1", "endpoint2", "endpoint3"]
results = ripper.rip_multiple_endpoints(endpoint_names)
comparison = ripper.compare_endpoints(endpoint_names)
```

## Export Formats

### JSON Format
Standard metadata format, easy to parse and process.

```json
{
  "name": "gpt-3.5-turbo",
  "endpoint_url": "http://localhost:8000",
  "model_type": "llm",
  "architecture": "transformer",
  "capabilities": ["chat_completion", "text_generation"],
  "parameters": {
    "endpoint_type": "/v1/models",
    "usage": {...}
  }
}
```

### Python Format
Python configuration file, ready to import.

```python
MODEL_CONFIG = {
    "name": "gpt-3.5-turbo",
    "endpoint_url": "http://localhost:8000",
    "model_type": "llm",
    "capabilities": ["chat_completion"],
    ...
}

def get_model_config():
    return MODEL_CONFIG
```

### GGUF Format
Compatible with llama.cpp and other tools.
- Binary format
- Includes metadata headers
- Optimized for inference

### ONNX Format
Cross-platform neural network format.
- Metadata export with `.meta.json`
- Note: Full ONNX export requires model weights

## Visualization Features

### Response Time Analysis
Track and visualize endpoint response times over multiple requests.

### Capability Comparison
Bar charts showing capability counts across endpoints.

### Token Attention Heatmap
Visualize attention patterns (requires model access).

### Behavior Classification
Pie charts showing distribution of detected behaviors.

## Security & Ethics

### Ethical Consent
By default, AI Ripper requires ethical consent before scanning:

- Only scan endpoints you own or have permission to access
- Respect API rate limits and terms of service
- Do not use for malicious purposes
- Comply with all applicable laws

### Security Features
- SSL certificate verification (configurable)
- API key encryption in memory
- No storage of sensitive credentials
- Rate limiting support

## Advanced Configuration

### Settings File
Save your preferences in `ai_ripper_settings.json`:

```json
{
  "timeout": 30,
  "max_retries": 3,
  "scan_depth": 3,
  "adaptive_memory": true,
  "max_memory": 2048,
  "require_consent": true,
  "verify_ssl": true
}
```

### Memory Management
- **Adaptive Memory**: Automatically adjusts memory usage based on system resources
- **Max Memory**: Set maximum memory usage in MB
- Handles large models gracefully on limited hardware

### Performance Optimization
- Parallel endpoint scanning
- Efficient memory management
- Optimized for large-scale models
- Adaptive timeout handling

## Troubleshooting

### Common Issues

**Connection Refused:**
- Verify endpoint URL is correct
- Check if the endpoint is running
- Ensure no firewall blocking

**Timeout Errors:**
- Increase timeout setting
- Check network connectivity
- Verify endpoint is responsive

**Export Failed:**
- Ensure write permissions
- Check disk space
- Verify endpoint was successfully ripped

**SSL Errors:**
- Disable SSL verification in settings (for testing only)
- Install proper certificates
- Use HTTP instead of HTTPS for local testing

## Examples

### Example 1: Extract Local Model

```bash
# Start your local model server
python -m vllm.entrypoints.api_server --model gpt2

# Extract model info
python ai_ripper_cli.py rip http://localhost:8000 -o gpt2.json
```

### Example 2: Compare Cloud Providers

```bash
python ai_ripper_cli.py compare \
  https://api.openai.com \
  https://api.anthropic.com \
  https://api.cohere.ai \
  --output provider_comparison.json
```

### Example 3: Export for llama.cpp

```bash
python ai_ripper_cli.py rip http://localhost:8000 \
  -f gguf \
  -o model.gguf
```

## Integration with Kimi K2

AI Ripper integrates seamlessly with the Kimi K2 ecosystem:

```python
from kimi_forge_unified import KimiForgeUnified
from ai_ripper_core import AIRipper

# Use Kimi K2 with AI Ripper
system = KimiForgeUnified()
ripper = AIRipper()

# Extract and analyze models
# Use Kimi K2 for intelligent model selection
# Combine capabilities for enhanced AI workflows
```

## Contributing

We welcome contributions! Please see the main [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run tests
python -m pytest tests/
```

## License

AI Ripper is part of the Kimi K2 project and is released under the Modified MIT License.
See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: This file and inline code documentation
- **Issues**: [GitHub Issues](https://github.com/SpidermanTotro/Kimi-K2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SpidermanTotro/Kimi-K2/discussions)

## Roadmap

### Planned Features
- [ ] Advanced model analysis (architecture detection)
- [ ] Automatic model conversion utilities
- [ ] Cloud provider integrations
- [ ] Enhanced visualization tools
- [ ] Model performance benchmarking
- [ ] Automated security scanning
- [ ] Multi-language support
- [ ] Plugin system for extensibility

## Credits

Developed as part of the Kimi K2 project by the community.

Special thanks to:
- The Kimi Team at Moonshot AI for the foundation
- Contributors to the FORGE project
- The open-source AI community

---

**Version**: 1.0  
**Last Updated**: 2025-12-10  
**Status**: Production Ready
