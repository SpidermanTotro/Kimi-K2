.PHONY: all build test bench clean run install lint fmt help

# Binary name
BINARY_NAME=kimi-k2-example

# Go commands
GOCMD=go
GOBUILD=$(GOCMD) build
GOTEST=$(GOCMD) test
GOGET=$(GOCMD) get
GOMOD=$(GOCMD) mod
GOFMT=$(GOCMD) fmt
GOVET=$(GOCMD) vet

# Build flags
LDFLAGS=-ldflags "-s -w"

all: fmt lint test build

help:
	@echo "Kimi-K2 16GB GPT Model - Makefile"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make build      - Build the example binary"
	@echo "  make test       - Run all tests"
	@echo "  make bench      - Run all benchmarks"
	@echo "  make run        - Build and run the example"
	@echo "  make fmt        - Format all Go code"
	@echo "  make lint       - Run Go vet"
	@echo "  make install    - Install dependencies"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make coverage   - Run tests with coverage"
	@echo "  make all        - Format, lint, test, and build"
	@echo ""

install:
	@echo "Installing dependencies..."
	$(GOMOD) download
	$(GOMOD) tidy
	@echo "Dependencies installed successfully!"

build: install
	@echo "Building example..."
	$(GOBUILD) $(LDFLAGS) -o bin/$(BINARY_NAME) examples/basic_usage.go
	@echo "Build complete: bin/$(BINARY_NAME)"

run: build
	@echo "Running example..."
	./bin/$(BINARY_NAME)

test: install
	@echo "Running tests..."
	$(GOTEST) -v -race ./...

test-short: install
	@echo "Running short tests..."
	$(GOTEST) -v -short ./...

bench: install
	@echo "Running benchmarks..."
	$(GOTEST) -bench=. -benchmem ./...

coverage: install
	@echo "Running tests with coverage..."
	$(GOTEST) -v -race -coverprofile=coverage.out -covermode=atomic ./...
	$(GOCMD) tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report generated: coverage.html"

fmt:
	@echo "Formatting code..."
	$(GOFMT) ./...
	@echo "Code formatted successfully!"

lint: fmt
	@echo "Running linter..."
	$(GOVET) ./...
	@echo "Linting complete!"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf bin/
	rm -f coverage.out coverage.html
	rm -f model_config.json tokenizer_vocab.json
	@echo "Clean complete!"

# Docker targets (optional)
docker-build:
	@echo "Building Docker image..."
	docker build -t kimi-k2:latest .

docker-run:
	@echo "Running in Docker..."
	docker run --rm kimi-k2:latest

# Development targets
dev-setup: install
	@echo "Setting up development environment..."
	@echo "Development setup complete!"

.DEFAULT_GOAL := help
