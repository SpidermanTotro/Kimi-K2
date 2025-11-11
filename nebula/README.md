# Nebula OS - Linux-like System for Kimi-K2

Welcome to Project Nebula! This is a comprehensive Linux-like operating system built on top of the Kimi-K2 repository.

## Quick Start

```bash
# Build the system
make build

# Run tests
make test

# Run the shell
make run-shell

# Run the kernel
make run-kernel

# Try the package manager
python3 nebula/package_manager/npm.py available
```

## Components

- **Kernel** - Process management, memory management, and system services
- **Shell** - Interactive command-line interface with built-in commands
- **Package Manager** - Install, update, and manage software packages

## Documentation

For complete documentation, see [nebula/docs/README.md](docs/README.md)

## Examples

Run the example scripts to see Nebula in action:

```bash
# Kernel and process management
python3 nebula/examples/kernel_example.py

# Package manager workflow
python3 nebula/examples/package_manager_example.py
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│        User Applications            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│         Nebula Shell (CLI)          │
│  - Command execution                │
│  - Environment management           │
│  - Built-in commands                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Package Manager (NPM)          │
│  - Package installation             │
│  - Dependency resolution            │
│  - Repository management            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│        Nebula Kernel                │
│  - Process scheduling               │
│  - Memory management                │
│  - System resources                 │
└─────────────────────────────────────┘
```

## Features

### Kernel
- ✅ Process creation and management
- ✅ Round-robin scheduler
- ✅ Memory allocation and tracking
- ✅ System boot and shutdown
- ✅ Process state management

### Shell
- ✅ Built-in commands (cd, ls, pwd, cat, etc.)
- ✅ Environment variables
- ✅ Command history
- ✅ External command execution
- ✅ Error handling

### Package Manager
- ✅ Package installation and removal
- ✅ Dependency resolution
- ✅ Package database
- ✅ Search and info commands
- ✅ Version management

## Requirements

- Python 3.7+
- Make (optional)

## License

Modified MIT License (same as Kimi-K2)

## Contributing

Contributions welcome! Please see the main repository guidelines.
