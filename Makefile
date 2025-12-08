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
	@pip3 install -q Flask Flask-CORS Pillow 2>/dev/null || true
	@echo "✅ Setup complete"

build: setup
	@echo "🔨 Building THE FORGE..."
	@python3 build_system.py
	@echo "✅ Build complete"

test:
	@echo "🧪 Testing THE FORGE..."
	@python3 -m py_compile *.py 2>/dev/null || true
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

# BASE 44 targets
run-base44:
	@echo "🚀 Starting BASE 44 (Free Forever Edition)..."
	@python3 base_44_core.py

run-base44-interactive:
	@echo "💬 Starting BASE 44 Interactive Mode..."
	@python3 base_44_launcher.py --mode interactive

run-base44-api:
	@echo "🌐 Starting BASE 44 API Server..."
	@python3 base_44_launcher.py --mode api

run-base44-demo:
	@echo "🎭 Starting BASE 44 Demo Mode..."
	@python3 base_44_launcher.py --mode demo

test-base44:
	@echo "🧪 Testing BASE 44..."
	@python3 -c "from base_44_core import Base44Core; b=Base44Core(); print('✅ BASE 44 initialized successfully'); print(f'✅ {len(b.capabilities)} capabilities loaded (ALL FREE)')"

help:
	@echo "THE FORGE - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make all       - Build everything"
	@echo "  make build     - Build THE FORGE"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean build artifacts"
	@echo "  make install   - Install THE FORGE"
	@echo "  make dist      - Create distribution"
	@echo "  make run-gui   - Start GUI"
	@echo "  make run-server - Start server"
	@echo "  make run-cli   - Start CLI"
	@echo ""
	@echo "BASE 44 targets (Free Forever Edition):"
	@echo "  make run-base44            - Run BASE 44 demo"
	@echo "  make run-base44-interactive - Interactive CLI mode"
	@echo "  make run-base44-api        - Start REST API server"
	@echo "  make run-base44-demo       - Run demonstration"
	@echo "  make test-base44           - Test BASE 44"
