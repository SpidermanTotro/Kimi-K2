# THE FORGE - Builder Documentation

## Quick Start

### Build Everything
```bash
# Using Make (recommended)
make all

# Or using Python directly
python3 build_system.py
```

### Download Distribution
After building, find the distribution ZIP in the `dist/` directory:
```bash
ls -lh dist/
```

## Multi-Language Support

THE FORGE is built with multiple programming languages:

### Python (Core AI & Backend)
- Main implementation language
- AI models and algorithms
- Web server (Flask)
- CLI interface

### JavaScript/Node.js (Frontend & Web)
- Web GUI components
- Interactive interfaces
- Real-time features

### C++ (Performance-Critical)
- Video processing
- Image manipulation
- High-performance computations

### Rust (Systems Programming)
- Memory-safe core components
- Concurrent processing
- Low-level optimizations

### Go (Services & Tools)
- Microservices
- CLI tools
- Network services

## Build Commands

```bash
# Build all components
make build

# Run tests
make test

# Clean build artifacts
make clean

# Create distribution
make dist

# Install locally
make install
```

## Running THE FORGE

### Start GUI
```bash
make run-gui
# Or: python3 forge_gui.py
```

### Start API Server
```bash
make run-server
# Or: python3 forge_server.py
```

### Start CLI
```bash
make run-cli
# Or: python3 forge_cli.py
```

## Distribution Package

The build creates a ZIP file containing:
- All Python source code
- Documentation files
- Configuration files
- Installation scripts
- README and guides

Download location: `dist/THE_FORGE_v1.0_YYYYMMDD.zip`

## System Requirements

### Minimum
- Python 3.8+
- 8GB RAM
- 10GB disk space

### Recommended
- Python 3.10+
- 16GB RAM
- 50GB disk space
- GPU (optional, for AI features)

## Installation from ZIP

1. Download the ZIP file from `dist/`
2. Extract to your preferred location
3. Run setup:
   ```bash
   pip install -r requirements.txt
   python3 forge_gui.py
   ```

## Advanced Building

### Build specific components
```bash
# Python only
python3 build_system.py

# With C++ components (requires CMake)
mkdir build && cd build
cmake ..
make

# With Rust components (requires Cargo)
cargo build --release

# With Go components
go build ./...
```

## Troubleshooting

### Build fails
- Ensure all dependencies are installed
- Check Python version (3.8+)
- Verify disk space

### Can't find distribution
- Check `dist/` directory
- Run `make dist` to create it

### Permission errors
- Use `sudo` for system-wide installation
- Or install to user directory

## Contributing

THE FORGE uses multiple languages:
- Python: Core AI, backend
- JavaScript: Frontend
- C++: Performance
- Rust: Systems
- Go: Services

Choose your preferred language and start building!

---

**THE FORGE: Built with ❤️ using Python, JavaScript, C++, Rust, Go, and more!**
