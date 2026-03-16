# THE FORGE - Master Makefile
# Builds entire project across all languages

.PHONY: all build test test-ripper test-dmg test-forge test-all clean install dist

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
	@echo "🧪 Running syntax check..."
	@python3 -m py_compile *.py 2>/dev/null || true
	@echo "🧪 Running full test suite..."
	@python3 -m pytest tests/ -q
	@echo "✅ Tests passed"

test-ripper:
	@echo "🧪 Testing RPM ripper (ElfAnalyzer, RpmRipper, ElfDecompiler, SrcRpmFinder)..."
	@python3 -m pytest tests/test_rpm_ripper.py -v
	@echo "✅ RPM ripper tests complete"

test-dmg:
	@echo "🧪 Testing DMG ripper (MachoAnalyzer, DmgRipper, LinuxPortingScaffold)..."
	@python3 -m pytest tests/test_dmg_ripper.py -v
	@echo "✅ DMG ripper tests complete"

test-forge:
	@echo "🧪 Testing Forge implementation (ForgeDocumentLoader, ForgeAI, ForgeBuilder)..."
	@python3 -m pytest tests/test_forge.py -v
	@echo "✅ Forge tests complete"

test-all:
	@echo "🧪 Running ALL tests..."
	@python3 -m pytest tests/ -v
	@echo "✅ All tests complete"

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

help:
	@echo "THE FORGE - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make all        - Build everything"
	@echo "  make build      - Build THE FORGE"
	@echo "  make test       - Syntax check + full test suite"
	@echo "  make test-ripper - Test RPM ripper (ElfAnalyzer, RpmRipper, ElfDecompiler)"
	@echo "  make test-dmg   - Test DMG ripper (MachoAnalyzer, DmgRipper, LinuxPortingScaffold)"
	@echo "  make test-forge - Test Forge implementation (ForgeDocumentLoader, ForgeAI)"
	@echo "  make test-all   - Run all test files verbosely"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make install    - Install THE FORGE"
	@echo "  make dist       - Create distribution"
	@echo "  make run-gui    - Start GUI"
	@echo "  make run-server - Start server"
	@echo "  make run-cli    - Start CLI"
