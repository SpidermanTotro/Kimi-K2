# Kimi-K2 Unified Framework

A comprehensive, modular AI framework that consolidates animation tools, Linux-style commands, GPT model optimizations, and collaboration features into a single cohesive system.

## Features

### 🎬 Animation Suite
- **Claymation & Video Generation**: Create professional-quality animations with AI-powered tools
- **Timeline Editor**: Precise control over animation sequences with drag-and-drop interface
- **Quality Presets**: Choose from draft, TV, or cinema quality settings
- **AI Optimization**: Automatic frame optimization and intelligent interpolation

### 💻 Command Interface
- **Linux-Style Commands**: Familiar command-line interface for developers
- **AI Script Generation**: Generate scripts from natural language descriptions
- **Custom Commands**: Extensible command system for workflow automation
- **Safe Execution**: Built-in safety controls for dangerous operations

### 🤖 AI Models
- **Dual Model System**: 
  - Lightweight (1B parameters, 2GB memory): Fast inference for quick tasks
  - Heavy (32B parameters, 16GB memory): Advanced capabilities for complex tasks
- **Memory Optimization**: Intelligent memory management and 16GB-optimized models
- **Scalable Architecture**: Automatic model switching based on task requirements

### 🤝 Collaboration
- **Multi-User Support**: Real-time collaboration across all modules
- **Session Management**: Create and join collaborative sessions
- **Shared State**: Synchronized state across all connected users
- **Concurrent Users**: Support for up to 10 simultaneous users (configurable)

### 🖥️ Unified Interfaces
- **Modern CLI**: Feature-rich command-line interface with Click
- **Desktop UI**: Cross-platform GUI built with Tkinter
- **Tutorial System**: Built-in walkthroughs for new users
- **Real-time Feedback**: Instant visual feedback for all operations

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev,ui,animation]"
```

## Quick Start

### Using the CLI

```bash
# Initialize configuration
kimi-k2 init

# Show framework information
kimi-k2 info

# Create an animation project
kimi-k2 animation create my_project --fps 30 --quality tv

# Generate text with AI
kimi-k2 model generate "Explain quantum computing" --model lightweight

# Execute a command
kimi-k2 cmd exec help

# Generate a script
kimi-k2 cmd gen-script "backup database daily"
```

### Using the Desktop UI

```bash
# Launch the desktop interface
python -m kimi_k2.ui.desktop
```

### Using as a Library

```python
from kimi_k2 import Framework, Config

# Create and initialize framework
framework = Framework()
framework.initialize()

# Use animation suite
animation = framework.get_module('animation')
project = animation.create_project(name="demo", fps=30)

# Use AI models
models = framework.get_module('models')
result = models.generate("Write a story about AI")

# Execute commands
commands = framework.get_module('commands')
result = commands.execute_command("help")

# Cleanup
framework.shutdown()
```

## Configuration

Create a configuration file to customize the framework:

```bash
kimi-k2 init --output my-config.yaml
```

Example configuration:

```yaml
animation:
  enabled: true
  output_dir: output/animations
  default_fps: 30
  quality_preset: tv
  max_duration: 300

commands:
  enabled: true
  shell_mode: bash
  script_dir: scripts
  allow_dangerous: false

models:
  enabled: true
  default_model: lightweight
  model_cache_dir: .cache/models
  max_memory_gb: 16
  use_optimization: true

ui:
  cli_enabled: true
  desktop_enabled: true
  theme: dark
  show_tutorials: true

collaboration:
  enabled: false
  server_host: localhost
  server_port: 8080
  max_users: 10
```

Use your configuration:

```bash
kimi-k2 --config my-config.yaml info
```

## Architecture

The framework follows a modular architecture with clear separation of concerns:

```
kimi-k2-framework/
├── src/kimi_k2/
│   ├── core/           # Core framework and configuration
│   ├── animation/      # Animation suite module
│   ├── commands/       # Command interface module
│   ├── models/         # AI models module
│   ├── collaboration/  # Multi-user collaboration
│   ├── ui/             # Desktop UI
│   ├── cli/            # Command-line interface
│   └── tests/          # Comprehensive test suite
```

### Modular Design

Each module can be independently enabled or disabled through configuration. This allows you to:
- Use only the features you need
- Reduce memory footprint
- Optimize for specific use cases
- Extend with custom modules

## Testing

The framework includes comprehensive tests with 90%+ coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=kimi_k2 --cov-report=html

# Run specific test file
pytest src/kimi_k2/tests/test_core.py

# Run tests for specific module
pytest src/kimi_k2/tests/test_animation.py -v
```

## Performance Benchmarking

Benchmark the framework components:

```python
from kimi_k2 import Framework
import time

framework = Framework()
framework.initialize()

# Benchmark animation rendering
animation = framework.get_module('animation')
project = animation.create_project(name="benchmark")

start = time.time()
animation.render_project("benchmark")
print(f"Render time: {time.time() - start:.2f}s")

# Benchmark AI generation
models = framework.get_module('models')
models.load_model("lightweight")

start = time.time()
result = models.generate("Test prompt")
print(f"Generation time: {time.time() - start:.2f}s")

framework.shutdown()
```

## API Reference

### Core Framework

- `Framework()`: Main framework class
  - `initialize()`: Initialize all enabled modules
  - `get_module(name)`: Get a specific module
  - `shutdown()`: Cleanup and shutdown

### Animation Suite

- `AnimationSuite.create_project()`: Create new animation project
- `AnimationSuite.render_project()`: Render project to video
- `TimelineEditor.add_clip()`: Add clip to timeline
- `AnimationOptimizer.optimize_frames()`: Apply AI optimizations

### Command Interface

- `CommandInterface.execute_command()`: Execute a command
- `CommandInterface.register_command()`: Register custom command
- `ScriptGenerator.generate_script()`: Generate script from description

### Model Manager

- `ModelManager.load_model()`: Load an AI model
- `ModelManager.generate()`: Generate text
- `ModelManager.list_models()`: List available models

### Collaboration Server

- `CollaborationServer.connect_user()`: Connect a user
- `CollaborationServer.create_session()`: Create collaboration session
- `CollaborationServer.update_shared_state()`: Update shared state

## Examples

See the `examples/` directory for complete examples:

- `examples/animation_workflow.py`: Complete animation pipeline
- `examples/command_automation.py`: Command automation examples
- `examples/model_comparison.py`: Compare lightweight vs heavy models
- `examples/collaborative_editing.py`: Multi-user collaboration demo

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Modified MIT License - see [LICENSE](LICENSE) file for details.

## Support

- Documentation: [https://moonshotai.github.io/Kimi-K2/](https://moonshotai.github.io/Kimi-K2/)
- Issues: [GitHub Issues](https://github.com/SpidermanTotro/Kimi-K2/issues)
- Email: [support@moonshot.cn](mailto:support@moonshot.cn)

## Acknowledgments

Built on top of the Kimi-K2 AI model by Moonshot AI. Special thanks to all contributors and the open-source community.
