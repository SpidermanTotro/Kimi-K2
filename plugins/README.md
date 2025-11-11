# Kimi K2 Plugin System

This directory contains the plugin system for Kimi K2, enabling seamless integration of external modules and APIs.

## Architecture

The plugin system is designed with modularity and extensibility in mind:

```
plugins/
├── core/           # Core plugin system implementation
├── examples/       # Example plugins
└── templates/      # Plugin templates for development
```

## Features

- **Dynamic Plugin Loading**: Load and unload plugins at runtime
- **API Integration**: Seamless integration with external APIs
- **Plugin Registry**: Centralized plugin discovery and management
- **Dependency Management**: Automatic handling of plugin dependencies
- **Testing Framework**: Built-in testing tools for plugin validation

## Quick Start

### Creating a Plugin

1. Use the plugin template:
```bash
python core/create_plugin.py --name my_plugin --type tool
```

2. Implement your plugin logic in the generated files

3. Test your plugin:
```bash
python core/test_plugin.py --plugin my_plugin
```

4. Register your plugin:
```bash
python core/register_plugin.py --plugin my_plugin
```

### Using a Plugin

```python
from plugins.core.loader import PluginLoader

# Initialize plugin loader
loader = PluginLoader()

# Load a plugin
plugin = loader.load_plugin("my_plugin")

# Use the plugin
result = plugin.execute(input_data)
```

## Plugin Types

- **Tool Plugins**: Extend Kimi K2's tool-calling capabilities
- **Data Plugins**: Add new data sources and processors
- **Model Plugins**: Integrate custom models or adapters
- **API Plugins**: Connect to external services

## Plugin Development Guide

See [templates/DEVELOPMENT.md](templates/DEVELOPMENT.md) for detailed development guidelines.

## Testing Framework

All plugins can be tested using the modularity testing framework:

```bash
# Run all tests for a plugin
pytest tests/test_<plugin_name>.py

# Run interactive tests
python core/interactive_test.py --plugin <plugin_name>
```

## Contributing

See [../community/templates/PLUGIN_SUBMISSION.md](../community/templates/PLUGIN_SUBMISSION.md) for plugin submission guidelines.
