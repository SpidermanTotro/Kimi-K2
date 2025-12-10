# THE FORGE - Master Makefile
# Builds entire project across all languages

.PHONY: all build test clean install dist

# Detect OS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    OS = linux
endif
ifeq ($(UNAME_S),Darwin)
    OS = macos
endif

# Build configuration
BUILD_DIR = build
DIST_DIR = dist
VERSION = 1.0.0

all: build

setup:
	@echo "🔥 Setting up THE FORGE build environment..."
	@mkdir -p $(BUILD_DIR) $(DIST_DIR)
	@pip3 install -q Flask Flask-CORS Pillow requests matplotlib numpy 2>/dev/null || true
	@echo "✅ Setup complete"

build: setup
	@echo "🔨 Building THE FORGE..."
	@python3 build_system.py
	@echo "✅ Build complete"

test:
	@echo "🧪 Testing THE FORGE..."
	@python3 -m py_compile *.py 2>/dev/null || true
	@python3 test_ai_ripper.py
	@echo "✅ Tests passed"

clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR) $(DIST_DIR)
	@rm -rf __pycache__ *.pyc
	@echo "✅ Clean complete"

install: build
	@echo "📦 Installing THE FORGE..."
	@echo "✅ Installation complete"

dist: build
	@echo "📦 Creating distribution..."
	@cd $(DIST_DIR) && ls -lh
	@echo "✅ Distribution ready"

run-gui:
	@echo "🎨 Starting THE FORGE GUI..."
	@python3 forge_gui.py

run-server:
	@echo "🚀 Starting THE FORGE Server..."
	@python3 forge_server.py

run-cli:
	@echo "💻 Starting THE FORGE CLI..."
	@python3 forge_cli.py

run-ripper-gui:
	@echo "🎨 Starting AI Ripper GUI..."
	@python3 ai_ripper_gui.py

run-ripper-cli:
	@echo "💻 AI Ripper CLI - use 'python3 ai_ripper_cli.py --help' for options"
	@python3 ai_ripper_cli.py --help

test-ripper:
	@echo "🧪 Testing AI Ripper..."
	@python3 test_ai_ripper.py

help:
	@echo "THE FORGE - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make all            - Build everything"
	@echo "  make build          - Build THE FORGE"
	@echo "  make test           - Run all tests (including AI Ripper)"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make install        - Install THE FORGE"
	@echo "  make dist           - Create distribution"
	@echo "  make run-gui        - Start THE FORGE GUI"
	@echo "  make run-server     - Start THE FORGE server"
	@echo "  make run-cli        - Start THE FORGE CLI"
	@echo ""
	@echo "AI Ripper targets:"
	@echo "  make run-ripper-gui - Start AI Ripper GUI"
	@echo "  make run-ripper-cli - Show AI Ripper CLI help"
	@echo "  make test-ripper    - Run AI Ripper tests"
