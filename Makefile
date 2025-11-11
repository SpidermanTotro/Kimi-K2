# Nebula OS Makefile
# Build system for Nebula Linux-like OS

PYTHON := python3
BUILD_SCRIPT := nebula/build/build.py
PREFIX := /usr/local

.PHONY: all build clean test install package help

# Default target
all: build test package

# Build all components
build:
	@echo "Building Nebula OS..."
	$(PYTHON) $(BUILD_SCRIPT) build

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	$(PYTHON) $(BUILD_SCRIPT) clean

# Run tests
test:
	@echo "Running tests..."
	$(PYTHON) $(BUILD_SCRIPT) test

# Install to system
install:
	@echo "Installing Nebula OS to $(PREFIX)..."
	$(PYTHON) $(BUILD_SCRIPT) install --prefix $(PREFIX)

# Create distribution package
package:
	@echo "Creating distribution package..."
	$(PYTHON) $(BUILD_SCRIPT) package

# Run the kernel
run-kernel:
	@echo "Starting Nebula Kernel..."
	$(PYTHON) nebula/kernel/kernel_module.py

# Run the shell
run-shell:
	@echo "Starting Nebula Shell..."
	$(PYTHON) nebula/cli/shell.py

# Run package manager
run-pkg:
	@echo "Starting Nebula Package Manager..."
	$(PYTHON) nebula/package_manager/npm.py --help

# Help
help:
	@echo "Nebula OS Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  all        - Build, test, and package (default)"
	@echo "  build      - Build all components"
	@echo "  clean      - Clean build artifacts"
	@echo "  test       - Run tests"
	@echo "  install    - Install to system (requires sudo)"
	@echo "  package    - Create distribution package"
	@echo "  run-kernel - Run the Nebula kernel"
	@echo "  run-shell  - Run the Nebula shell"
	@echo "  run-pkg    - Run the package manager"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make test"
	@echo "  sudo make install PREFIX=/usr/local"
	@echo "  make run-shell"
