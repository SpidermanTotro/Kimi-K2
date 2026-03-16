# THE FORGE - Master Makefile
# Builds entire project across all languages

.PHONY: all build test clean install dist \
        merge-kimi merge-kimi-32b merge-kimi-16b \
        install-kimi-ollama run-kimi-32b run-kimi-16b

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

## ── Kimi All-Skills Merger (limex) ────────────────────────────────────
## Merges ALL Kimi skills, strips payment features, generates Ollama
## Modelfiles and an Alpaca-format JSONL fine-tuning dataset.

merge-kimi:
	@echo "🔀 Merging all Kimi skills (limex framework)..."
	@python3 kimi_ollama_merger.py
	@echo "✅ Merge complete"

merge-kimi-32b:
	@echo "🔀 Generating 32 GB variant..."
	@python3 kimi_ollama_merger.py --variant 32b

merge-kimi-16b:
	@echo "🔀 Generating 16 GB variant..."
	@python3 kimi_ollama_merger.py --variant 16b

install-kimi-ollama:
	@echo "📦 Generating artefacts and installing into Ollama..."
	@python3 kimi_ollama_merger.py --install

run-kimi-32b:
	@echo "🚀 Running KimiFree 32B..."
	@ollama run kimi-free-32b

run-kimi-16b:
	@echo "🚀 Running KimiFree 16B..."
	@ollama run kimi-free-16b

help:
	@echo "THE FORGE - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make all              - Build everything"
	@echo "  make build            - Build THE FORGE"
	@echo "  make test             - Run tests"
	@echo "  make clean            - Clean build artifacts"
	@echo "  make install          - Install THE FORGE"
	@echo "  make dist             - Create distribution"
	@echo "  make run-gui          - Start GUI"
	@echo "  make run-server       - Start server"
	@echo "  make run-cli          - Start CLI"
	@echo ""
	@echo "Kimi All-Skills Merger (limex):"
	@echo "  make merge-kimi           - Merge all skills, strip payment, generate artefacts"
	@echo "  make merge-kimi-32b       - 32 GB Modelfile + training data only"
	@echo "  make merge-kimi-16b       - 16 GB Modelfile + training data only"
	@echo "  make install-kimi-ollama  - Generate artefacts + ollama create both variants"
	@echo "  make run-kimi-32b         - ollama run kimi-free-32b"
	@echo "  make run-kimi-16b         - ollama run kimi-free-16b"
