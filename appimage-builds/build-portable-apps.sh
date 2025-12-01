#!/bin/bash
# Build Portable Applications (No FUSE required)
# Creates standalone executable directories

set -e

echo "🚀 Building Portable Applications"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Build THE FORGE AI Portable
build_forge_portable() {
    print_info "Building THE FORGE AI Portable..."
    
    APP_DIR="TheForgeAI-Portable"
    rm -rf "$APP_DIR"
    mkdir -p "$APP_DIR"
    
    # Copy files
    cp -r ../web_interface "$APP_DIR/"
    cp ../forge_server.py "$APP_DIR/"
    cp ../forge_cli.py "$APP_DIR/"
    cp ../forge_implementation.py "$APP_DIR/"
    cp -r ../live_programs "$APP_DIR/"
    cp ../requirements.txt "$APP_DIR/"
    
    # Create launcher
    cat > "$APP_DIR/run-forge.sh" << 'EOF'
#!/bin/bash
# THE FORGE AI Launcher

cd "$(dirname "$0")/web_interface"

echo "🔥 Starting THE FORGE AI..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q flask flask-cors flask-socketio python-socketio
else
    source venv/bin/activate
fi

# Start server
echo "Starting server on http://localhost:9001"
python3 server.py &
SERVER_PID=$!

sleep 2

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:9001"
elif command -v firefox &> /dev/null; then
    firefox "http://localhost:9001"
else
    echo "Open http://localhost:9001 in your browser"
fi

echo ""
echo "Press Ctrl+C to stop the server"
wait $SERVER_PID
EOF
    
    chmod +x "$APP_DIR/run-forge.sh"
    
    # Create README
    cat > "$APP_DIR/README.txt" << 'EOF'
THE FORGE AI - Portable Edition
================================

To run:
1. Open terminal in this directory
2. Run: ./run-forge.sh
3. Browser will open automatically

Requirements:
- Python 3.7+
- Internet connection (first run only, for dependencies)

The application will run on http://localhost:9001
EOF
    
    # Create archive
    tar -czf TheForgeAI-Portable.tar.gz "$APP_DIR"
    
    print_status "THE FORGE AI Portable created!"
    echo "   Output: TheForgeAI-Portable.tar.gz"
    echo "   Size: $(du -h TheForgeAI-Portable.tar.gz | cut -f1)"
}

# Build NEXUS AI Portable
build_nexus_portable() {
    print_info "Building NEXUS AI Portable..."
    
    APP_DIR="NexusAI-Portable"
    rm -rf "$APP_DIR"
    mkdir -p "$APP_DIR"
    
    # Copy files
    cp -r ../nexus-ai/* "$APP_DIR/"
    
    # Create launcher
    cat > "$APP_DIR/run-nexus.sh" << 'EOF'
#!/bin/bash
# NEXUS AI Launcher

cd "$(dirname "$0")"

echo "🚀 Starting NEXUS AI..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3.11+ is required"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
else
    source venv/bin/activate
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY not set"
    echo "Please set it in .env file or export it"
    echo ""
fi

# Run Nexus AI
python3 main.py
EOF
    
    chmod +x "$APP_DIR/run-nexus.sh"
    
    # Create README
    cat > "$APP_DIR/README.txt" << 'EOF'
NEXUS AI - Portable Edition
============================

Setup:
1. Copy .env.example to .env
2. Add your OpenAI API key to .env
3. Run: ./run-nexus.sh

Requirements:
- Python 3.11+
- OpenAI API key
- Internet connection

Features:
- Multi-agent AI system
- GPT-4 and o1 reasoning models
- Safe code execution
- Advanced reasoning capabilities
EOF
    
    # Create archive
    tar -czf NexusAI-Portable.tar.gz "$APP_DIR"
    
    print_status "NEXUS AI Portable created!"
    echo "   Output: NexusAI-Portable.tar.gz"
    echo "   Size: $(du -h NexusAI-Portable.tar.gz | cut -f1)"
}

# Main
main() {
    build_forge_portable
    echo ""
    build_nexus_portable
    
    echo ""
    echo "===================================="
    echo -e "${GREEN}✓ Build complete!${NC}"
    echo "===================================="
    echo ""
    echo "Created:"
    echo "  • TheForgeAI-Portable.tar.gz"
    echo "  • NexusAI-Portable.tar.gz"
    echo ""
    echo "To use:"
    echo "  1. Extract: tar -xzf <filename>.tar.gz"
    echo "  2. Run: cd <directory> && ./run-*.sh"
    echo ""
}

main