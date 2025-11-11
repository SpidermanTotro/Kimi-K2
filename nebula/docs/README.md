# Project Nebula: Linux-like System for Kimi-K2

## Overview

Project Nebula is a comprehensive enhancement to the Kimi-K2 repository that adds the capability to build a full-scale Linux-like operating system. It includes kernel-level components, a command-line interface, and a package management system.

## Architecture

Nebula OS consists of three main components:

### 1. Kernel Module (`nebula/kernel/`)
The kernel provides core system functionality:
- **Process Management**: Process creation, scheduling, and termination
- **Memory Management**: Memory allocation, deallocation, and tracking
- **System Information**: Uptime, resource usage, and system statistics

**Features:**
- Process Control Blocks (PCB) with state management
- Round-robin process scheduler
- Memory manager with allocation tracking
- System boot and shutdown procedures

### 2. Command-Line Interface (`nebula/cli/`)
A fully functional shell implementation:
- **Built-in Commands**: cd, pwd, ls, cat, mkdir, rm, touch, echo, etc.
- **Environment Variables**: Support for environment variable manipulation
- **Command History**: Track and display command history
- **External Commands**: Execute system commands
- **Pipeline Support**: Basic pipe functionality (in development)

**Features:**
- Interactive command-line interface
- Tab-completion ready structure
- Custom prompt
- Error handling and feedback

### 3. Package Manager (`nebula/package_manager/`)
A simple yet effective package management system:
- **Install/Remove**: Install and remove packages
- **Dependencies**: Automatic dependency resolution
- **Repository**: Package repository with metadata
- **Database**: JSON-based package database
- **Search**: Search for packages by name or description

**Features:**
- Dependency resolution and installation
- Package metadata tracking
- Version management
- Size calculation and reporting

## Installation

### Prerequisites
- Python 3.7 or higher
- Make (optional, for using Makefile)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SpidermanTotro/Kimi-K2.git
   cd Kimi-K2
   ```

2. **Build the system:**
   ```bash
   make build
   ```

3. **Run tests:**
   ```bash
   make test
   ```

4. **Install (optional):**
   ```bash
   sudo make install PREFIX=/usr/local
   ```

### Manual Build

If you prefer not to use Make:

```bash
python3 nebula/build/build.py build
python3 nebula/build/build.py test
python3 nebula/build/build.py install --prefix /usr/local
```

## Usage

### Running the Kernel

```bash
python3 nebula/kernel/kernel_module.py
```

The kernel will:
1. Boot and initialize system resources
2. Create the init process
3. Display system information
4. Allow you to interact with it

Example output:
```
Booting Nebula Kernel v0.1.0...
Kernel booted successfully at Mon Nov 11 04:17:00 2025
Total memory: 1024 MB

System Information:
  kernel_version: 0.1.0
  uptime: 0.001
  memory: {'total': 1073741824, 'allocated': 1048576, 'free': 1072693248}
  processes: 1
```

### Running the Shell

```bash
python3 nebula/cli/shell.py
```

Available commands:
- `help` - Display available commands
- `pwd` - Print working directory
- `cd <dir>` - Change directory
- `ls [path]` - List directory contents
- `cat <file>` - Display file contents
- `echo <text>` - Echo text to output
- `mkdir <dir>` - Create directory
- `touch <file>` - Create empty file
- `rm <file>` - Remove file
- `env` - Display environment variables
- `export KEY=VALUE` - Set environment variable
- `history` - Show command history
- `clear` - Clear screen
- `version` - Show version
- `exit` - Exit shell

Example session:
```
Nebula Shell v0.1.0
Type 'help' for available commands.

nebula> pwd
/home/user
nebula> ls
file1.txt
file2.txt
nebula> mkdir test
nebula> cd test
nebula> pwd
/home/user/test
nebula> exit
Goodbye!
```

### Using the Package Manager

```bash
python3 nebula/package_manager/npm.py <command> [options]
```

Available commands:
- `install <package>` - Install a package
- `remove <package>` - Remove a package
- `update [package]` - Update package(s)
- `list` - List installed packages
- `available` - List available packages
- `search <query>` - Search for packages
- `info <package>` - Show package information

Examples:

**List available packages:**
```bash
python3 nebula/package_manager/npm.py available
```

**Install a package:**
```bash
python3 nebula/package_manager/npm.py install nebula-utils
```

**Search for packages:**
```bash
python3 nebula/package_manager/npm.py search network
```

**List installed packages:**
```bash
python3 nebula/package_manager/npm.py list
```

**Show package info:**
```bash
python3 nebula/package_manager/npm.py info nebula-web
```

## Development

### Project Structure

```
nebula/
├── kernel/
│   └── kernel_module.py    # Kernel implementation
├── cli/
│   └── shell.py            # Shell implementation
├── package_manager/
│   └── npm.py              # Package manager
├── build/
│   └── build.py            # Build system
├── examples/
│   └── (example scripts)
└── docs/
    └── (additional documentation)
```

### Adding New Features

#### Adding a New Kernel Feature

Edit `nebula/kernel/kernel_module.py` and add your feature to the `NebulaKernel` class.

#### Adding a New Shell Command

Edit `nebula/cli/shell.py`:
1. Add a method `cmd_yourcommand(self, args: List[str]) -> int`
2. Add it to the `self.builtins` dictionary in `__init__`

Example:
```python
def cmd_hello(self, args: List[str]) -> int:
    """Say hello"""
    name = args[0] if args else "World"
    print(f"Hello, {name}!")
    return 0
```

#### Adding a New Package

Edit `nebula/package_manager/npm.py` and add your package to the `_create_sample_repository` method:

```python
"your-package": Package(
    name="your-package",
    version="1.0.0",
    description="Your package description",
    dependencies=["dependency1", "dependency2"],
    size=1024 * 1024  # 1MB
),
```

### Testing

Run the test suite:
```bash
make test
```

Or manually:
```bash
python3 nebula/build/build.py test
```

## Examples

See the `nebula/examples/` directory for example scripts and use cases.

## Building a Distribution

Create a distributable package:
```bash
make package
```

This creates a `.tar.gz` file in the `dist/` directory.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## Roadmap

Future enhancements planned:
- [ ] Full pipeline support in shell
- [ ] Network stack implementation
- [ ] File system abstraction
- [ ] Device driver framework
- [ ] Multi-threading support
- [ ] Inter-process communication (IPC)
- [ ] Remote package repository support
- [ ] Package signing and verification
- [ ] System service management
- [ ] Boot loader implementation

## License

This enhancement follows the same license as the main Kimi-K2 project (Modified MIT License).

## Support

For issues, questions, or contributions related to Project Nebula, please open an issue on GitHub.

## Acknowledgments

Project Nebula is inspired by modern Linux distributions and educational operating systems. It aims to provide a learning platform for understanding OS concepts while maintaining practical utility.
