#!/bin/bash
# Build Windows Portable Applications
# Creates .bat launchers for Windows

set -e

echo "🪟 Building Windows Portable Applications"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Build THE FORGE AI Windows
build_forge_windows() {
    print_info "Building THE FORGE AI for Windows..."
    
    APP_DIR="TheForgeAI-Windows"
    rm -rf "$APP_DIR"
    mkdir -p "$APP_DIR"
    
    # Copy files
    cp -r ../web_interface "$APP_DIR/"
    cp ../forge_server.py "$APP_DIR/"
    cp ../forge_cli.py "$APP_DIR/"
    cp ../forge_implementation.py "$APP_DIR/"
    cp -r ../live_programs "$APP_DIR/"
    cp ../requirements.txt "$APP_DIR/"
    
    # Create Windows launcher
    cat > "$APP_DIR/run-forge.bat" << 'EOF'
@echo off
REM THE FORGE AI Launcher for Windows

cd /d "%~dp0\web_interface"

echo.
echo 🔥 Starting THE FORGE AI...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q flask flask-cors flask-socketio python-socketio
) else (
    call venv\Scripts\activate.bat
)

REM Start server
echo Starting server on http://localhost:9001
echo.
start /B python server.py

timeout /t 2 /nobreak >nul

REM Open browser
start http://localhost:9001

echo.
echo Press Ctrl+C to stop the server
echo.
pause
EOF
    
    # Create README
    cat > "$APP_DIR/README.txt" << 'EOF'
THE FORGE AI - Windows Edition
===============================

To run:
1. Double-click run-forge.bat
2. Browser will open automatically

Requirements:
- Python 3.7+ (download from python.org)
- Internet connection (first run only)

The application will run on http://localhost:9001

Troubleshooting:
- If Python is not found, install it from python.org
- Make sure to check "Add Python to PATH" during installation
EOF
    
    # Create archive
    zip -q -r TheForgeAI-Windows.zip "$APP_DIR"
    
    print_status "THE FORGE AI Windows created!"
    echo "   Output: TheForgeAI-Windows.zip"
    echo "   Size: $(du -h TheForgeAI-Windows.zip | cut -f1)"
}

# Build NEXUS AI Windows
build_nexus_windows() {
    print_info "Building NEXUS AI for Windows..."
    
    APP_DIR="NexusAI-Windows"
    rm -rf "$APP_DIR"
    mkdir -p "$APP_DIR"
    
    # Copy files
    cp -r ../nexus-ai/* "$APP_DIR/"
    
    # Create Windows launcher
    cat > "$APP_DIR/run-nexus.bat" << 'EOF'
@echo off
REM NEXUS AI Launcher for Windows

cd /d "%~dp0"

echo.
echo 🚀 Starting NEXUS AI...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3.11+ is required
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv" (
    echo Setting up virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -q -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Check for API key
if "%OPENAI_API_KEY%"=="" (
    echo.
    echo ⚠️  Warning: OPENAI_API_KEY not set
    echo Please set it in .env file
    echo.
)

REM Run Nexus AI
python main.py

pause
EOF
    
    # Create README
    cat > "$APP_DIR/README.txt" << 'EOF'
NEXUS AI - Windows Edition
===========================

Setup:
1. Copy .env to .env.local
2. Edit .env.local and add your OpenAI API key
3. Double-click run-nexus.bat

Requirements:
- Python 3.11+ (download from python.org)
- OpenAI API key
- Internet connection

Features:
- Multi-agent AI system
- GPT-4 and o1 reasoning models
- Safe code execution
- Advanced reasoning capabilities

Troubleshooting:
- If Python is not found, install it from python.org
- Make sure to check "Add Python to PATH" during installation
- Get OpenAI API key from platform.openai.com
EOF
    
    # Create archive
    zip -q -r NexusAI-Windows.zip "$APP_DIR"
    
    print_status "NEXUS AI Windows created!"
    echo "   Output: NexusAI-Windows.zip"
    echo "   Size: $(du -h NexusAI-Windows.zip | cut -f1)"
}

# Main
main() {
    build_forge_windows
    echo ""
    build_nexus_windows
    
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ Build complete!${NC}"
    echo "=========================================="
    echo ""
    echo "Created:"
    echo "  • TheForgeAI-Windows.zip"
    echo "  • NexusAI-Windows.zip"
    echo ""
    echo "To use on Windows:"
    echo "  1. Extract the ZIP file"
    echo "  2. Double-click run-*.bat"
    echo ""
}

main