# Plugin Template for Kimi K2

This directory contains templates for creating new plugins.

## Plugin Types

### Tool Plugin
Tool plugins extend Kimi K2's tool-calling capabilities with custom tools.

### API Plugin
API plugins integrate external services and APIs.

### Data Plugin
Data plugins add new data sources and processing capabilities.

### Model Plugin
Model plugins integrate custom models or adapters.

## Template Structure

```
plugin_name/
├── __init__.py       # Plugin implementation
├── config.yaml       # Plugin configuration
├── requirements.txt  # Plugin dependencies
├── tests/           # Plugin tests
│   └── test_plugin.py
└── README.md        # Plugin documentation
```

## Creating a New Plugin

1. Copy the appropriate template directory
2. Rename it to your plugin name
3. Update `__init__.py` with your implementation
4. Update `config.yaml` with your configuration
5. Add any dependencies to `requirements.txt`
6. Write tests in `tests/`
7. Update `README.md` with documentation

## Plugin Template Files

- `tool_plugin_template/` - Template for tool plugins
- `api_plugin_template/` - Template for API plugins
- `data_plugin_template/` - Template for data plugins
- `model_plugin_template/` - Template for model plugins

## Development Guidelines

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development guidelines.
