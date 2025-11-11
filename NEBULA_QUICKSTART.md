# Project Nebula - Installation and Quick Start Guide

## What is Project Nebula?

Project Nebula is a full-scale Linux-like operating system built on top of the Kimi-K2 repository. It provides:

- **Kernel Module**: Process and memory management
- **CLI Shell**: Interactive command-line interface
- **Package Manager**: Software installation and dependency management

## Installation

### Prerequisites
- Python 3.7 or higher
- Make (optional, but recommended)
- Git

### Quick Install

```bash
# Clone the repository
git clone https://github.com/SpidermanTotro/Kimi-K2.git
cd Kimi-K2

# Build the system
make build

# Run tests
make test
```

## Getting Started

### 1. Run the Comprehensive Demo

See all components in action:

```bash
python3 nebula/examples/comprehensive_demo.py
```

### 2. Try the Kernel

```bash
make run-kernel
# Or directly:
python3 nebula/kernel/kernel_module.py
```

**What you'll see:**
- System boot sequence
- Process creation and management
- Memory allocation tracking
- System information display

### 3. Try the Shell

```bash
make run-shell
# Or directly:
python3 nebula/cli/shell.py
```

**Available commands:**
```
help      - Show available commands
pwd       - Print working directory
cd        - Change directory
ls        - List files
cat       - Display file contents
mkdir     - Create directory
touch     - Create file
rm        - Remove file
echo      - Print text
env       - Show environment variables
export    - Set environment variable
history   - Show command history
clear     - Clear screen
version   - Show version
exit      - Exit shell
```

### 4. Try the Package Manager

```bash
# List available packages
python3 nebula/package_manager/npm.py available

# Install a package
python3 nebula/package_manager/npm.py install nebula-utils

# List installed packages
python3 nebula/package_manager/npm.py list

# Search for packages
python3 nebula/package_manager/npm.py search network

# Get package info
python3 nebula/package_manager/npm.py info nebula-web

# Remove a package
python3 nebula/package_manager/npm.py remove nebula-utils
```

## Examples

### Example 1: Process Management

```bash
python3 nebula/examples/kernel_example.py
```

This demonstrates:
- Creating multiple processes
- Memory allocation
- Process scheduling
- System monitoring

### Example 2: Package Management Workflow

```bash
python3 nebula/examples/package_manager_example.py
```

This demonstrates:
- Browsing available packages
- Installing packages with dependencies
- Searching for packages
- Removing packages
- Dependency checking

## Build System

### Makefile Targets

```bash
make build      # Build all components
make clean      # Clean build artifacts
make test       # Run tests
make install    # Install to system (requires sudo)
make package    # Create distribution package
make run-kernel # Run the kernel
make run-shell  # Run the shell
make help       # Show all available targets
```

### Manual Build

If you prefer not to use Make:

```bash
# Clean
python3 nebula/build/build.py clean

# Build
python3 nebula/build/build.py build

# Test
python3 nebula/build/build.py test

# Install (requires sudo)
sudo python3 nebula/build/build.py install --prefix /usr/local

# Create package
python3 nebula/build/build.py package
```

## Project Structure

```
nebula/
├── README.md                        # Quick start guide
├── __init__.py                      # Package initialization
├── kernel/                          # Kernel module
│   ├── kernel_module.py            # Main kernel implementation
│   └── __init__.py
├── cli/                            # Command-line interface
│   ├── shell.py                    # Shell implementation
│   └── __init__.py
├── package_manager/                # Package management
│   ├── npm.py                      # Package manager implementation
│   └── __init__.py
├── build/                          # Build system
│   └── build.py                    # Build script
├── examples/                       # Example scripts
│   ├── kernel_example.py           # Kernel demo
│   ├── package_manager_example.py  # Package manager demo
│   └── comprehensive_demo.py       # Complete demo
└── docs/                           # Documentation
    └── README.md                   # Detailed documentation
```

## Architecture

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

## Key Features

### Kernel
✅ Process creation and management  
✅ Round-robin scheduling algorithm  
✅ Memory allocation and tracking  
✅ System boot and shutdown  
✅ Process state management  
✅ Resource monitoring  

### Shell
✅ 15+ built-in commands  
✅ Environment variable support  
✅ Command history  
✅ External command execution  
✅ Tab-completion ready  
✅ Error handling  

### Package Manager
✅ Package installation/removal  
✅ Automatic dependency resolution  
✅ Package search and info  
✅ Version management  
✅ JSON-based package database  
✅ Size tracking and reporting  

## Troubleshooting

### Build Fails
```bash
# Make sure Python 3.7+ is installed
python3 --version

# Clean and rebuild
make clean
make build
```

### Tests Fail
```bash
# Check Python syntax
python3 -m py_compile nebula/kernel/kernel_module.py
python3 -m py_compile nebula/cli/shell.py
python3 -m py_compile nebula/package_manager/npm.py
```

### Import Errors
```bash
# Make sure you're in the right directory
cd /path/to/Kimi-K2

# Run from repository root
python3 nebula/examples/comprehensive_demo.py
```

## Next Steps

1. **Read the full documentation**: [nebula/docs/README.md](docs/README.md)
2. **Try the examples**: Run all example scripts
3. **Explore the shell**: Use `make run-shell` and try different commands
4. **Experiment with packages**: Install different package combinations
5. **Extend the system**: Add your own components!

## Contributing

Contributions are welcome! Areas for improvement:
- Additional shell commands
- Network stack implementation
- File system abstraction
- Device drivers
- Multi-threading support
- IPC mechanisms
- Remote package repositories

## Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation in `nebula/docs/`
- Review example scripts in `nebula/examples/`

## License

Modified MIT License (same as Kimi-K2)

---

**Project Nebula** - Building the future, one system call at a time. 🚀
