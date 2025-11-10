# Makefile for Kimi-K2 Animation AI Module

.PHONY: build clean test install examples help

# Default target
all: build

# Build the CLI tool
build:
	@echo "Building kimi-animation CLI..."
	cd animation && go build -o kimi-animation ./cli
	@echo "✓ Build complete: animation/kimi-animation"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f animation/kimi-animation
	rm -f animation/*.json
	rm -f animation/examples/output_*.json
	@echo "✓ Clean complete"

# Run tests
test:
	@echo "Running tests..."
	cd animation && go test ./...
	@echo "✓ Tests complete"

# Install dependencies
install:
	@echo "Installing Go dependencies..."
	cd animation && go mod download
	@echo "✓ Dependencies installed"

# Run examples
examples: build
	@echo "Running claymation example..."
	cd animation/examples && go run claymation_example.go
	@echo ""
	@echo "Running animation example..."
	cd animation/examples && go run animation_example.go
	@echo "✓ Examples complete"

# Run linting
lint:
	@echo "Running linters..."
	cd animation && go fmt ./...
	cd animation && go vet ./...
	@echo "✓ Linting complete"

# Generate documentation
docs:
	@echo "Generating documentation..."
	cd animation && go doc -all > docs/godoc.txt
	@echo "✓ Documentation generated"

# Quick demo
demo: build
	@echo "=== Kimi-K2 Animation AI Demo ==="
	@echo ""
	@echo "1. Listing available styles..."
	cd animation && ./kimi-animation claymation list-styles
	@echo ""
	@echo "2. Generating walk cycle..."
	cd animation && ./kimi-animation animation generate-loop walk demo_walk.json --type 3D
	@echo ""
	@echo "3. Creating humanoid rig..."
	cd animation && ./kimi-animation animation create-rig humanoid demo_rig.json
	@echo ""
	@echo "4. Analyzing example sequence..."
	cd animation && ./kimi-animation claymation analyze examples/example_sequence.json
	@echo ""
	@echo "✓ Demo complete!"

# Help target
help:
	@echo "Kimi-K2 Animation AI - Available targets:"
	@echo ""
	@echo "  make build     - Build the CLI tool"
	@echo "  make clean     - Clean build artifacts"
	@echo "  make test      - Run tests"
	@echo "  make install   - Install dependencies"
	@echo "  make examples  - Run example programs"
	@echo "  make lint      - Run linters"
	@echo "  make docs      - Generate documentation"
	@echo "  make demo      - Run a quick demo"
	@echo "  make help      - Show this help message"
	@echo ""
