# Changelog

All notable changes to the Kimi-K2 utilities and examples will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-10

### Added

#### Core Features
- **Enhanced KimiClient**: Python client with streaming, tool calling, and flexible configuration
- **ToolManager**: Automatic tool schema generation with decorator-based registration
- **Command Line Interface**: Interactive and single-message chat commands
- **Benchmark Runner**: Comprehensive latency and throughput testing tools

#### Examples
- `basic_chat.py`: Simple and multi-turn conversation examples
- `tool_calling.py`: Tool registration and usage demonstrations
- `code_assistant.py`: Code generation and review workflows
- `multi_agent.py`: Multi-agent conversation systems

#### Documentation
- **Tutorials**: Step-by-step guides for common use cases
- **API Reference**: Complete API documentation for all modules
- **Advanced Usage Guide**: Best practices and optimization patterns
- **Utilities Guide**: Overview of new features and capabilities

#### Testing
- Comprehensive unit tests for KimiClient
- Comprehensive unit tests for ToolManager
- Test configuration with pytest and coverage reporting
- 91% code coverage for core modules

#### Infrastructure
- Package structure with setuptools
- Development dependencies configuration
- Requirements file for easy installation
- .gitignore for Python projects
- Black code formatting
- Pytest configuration

### Features Detail

#### KimiClient
- Simple one-turn chat with `simple_chat()`
- Multi-turn conversations with `chat()`
- Streaming responses for better UX
- Automatic tool calling with `chat_with_tools()`
- Configurable temperature and token limits
- Support for custom parameters

#### ToolManager
- Decorator-based tool registration
- Automatic schema generation from Python functions
- Type inference for parameters
- Support for required and optional parameters
- Easy integration with KimiClient

#### CLI
- `kimi-cli chat`: Send single messages
- `kimi-cli interactive`: Start interactive sessions
- Support for system messages, temperature, and streaming
- Input from stdin for scripting
- Rich terminal formatting

#### Benchmarking
- Latency testing with statistical analysis
- Throughput testing over time
- JSON export of detailed results
- CLI tool for command-line benchmarking

### Performance
- Efficient streaming implementation
- Minimal overhead for tool calling
- Optimized for both interactive and batch use

### Documentation
- Over 40 pages of comprehensive documentation
- 15+ code examples
- Best practices and patterns
- Troubleshooting guides

## [Unreleased]

### Planned Features
- Async client implementation
- Advanced caching mechanisms
- More example applications
- Integration tests
- Performance optimizations
- Additional language bindings

---

## Version History

- **1.0.0** (2025-11-10): Initial release with comprehensive utilities and examples
