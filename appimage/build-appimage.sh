#!/bin/bash
# THE FORGE AI - AppImage Builder
# Creates self-contained Linux desktop application

set -e

echo "🔥 THE FORGE AI - AppImage Builder"
echo "=================================="
echo ""

# Configuration
APP_NAME="TheForgeAI"
APP_VERSION="2.0.0"
APP_DIR="TheForgeAI.AppDir"
BUILD_DIR="build"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v wget &> /dev/null; then
        missing_deps+=("wget")
    fi
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Install with: sudo apt-get install ${missing_deps[*]}"
        exit 1
    fi
    
    print_status "All dependencies found"
}

# Download AppImage tools
download_tools() {
    print_info "Downloading AppImage tools..."
    
    if [ ! -f "appimagetool-x86_64.AppImage" ]; then
        wget -q --show-progress https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
        chmod +x appimagetool-x86_64.AppImage
        print_status "Downloaded appimagetool"
    else
        print_status "appimagetool already downloaded"
    fi
}

# Create AppDir structure
create_appdir() {
    print_info "Creating AppDir structure..."
    
    # Clean previous build
    rm -rf "$APP_DIR"
    mkdir -p "$APP_DIR"
    
    # Create directory structure
    mkdir -p "$APP_DIR/usr/bin"
    mkdir -p "$APP_DIR/usr/lib"
    mkdir -p "$APP_DIR/usr/share/applications"
    mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
    mkdir -p "$APP_DIR/usr/share/metainfo"
    
    print_status "AppDir structure created"
}

# Copy application files
copy_files() {
    print_info "Copying application files..."
    
    # Copy web interface
    cp -r ../web_interface "$APP_DIR/usr/bin/"
    
    # Copy FORGE implementation
    cp ../forge_implementation.py "$APP_DIR/usr/bin/"
    cp ../forge_server.py "$APP_DIR/usr/bin/"
    cp ../forge_cli.py "$APP_DIR/usr/bin/"
    
    # Copy live programs
    cp -r ../live_programs "$APP_DIR/usr/bin/"
    
    # Copy docs
    cp -r ../docs "$APP_DIR/usr/bin/"
    
    print_status "Application files copied"
}

# Create launcher script
create_launcher() {
    print_info "Creating launcher script..."
    
    cat > "$APP_DIR/AppRun" << 'EOF'
#!/bin/bash
# THE FORGE AI Launcher

# Get the directory where the AppImage is mounted
APPDIR="$(dirname "$(readlink -f "$0")")"

# Set Python path
export PYTHONPATH="$APPDIR/usr/bin:$PYTHONPATH"

# Change to app directory
cd "$APPDIR/usr/bin/web_interface"

# Check if server is already running
if pgrep -f "python3.*server.py" > /dev/null; then
    echo "Server already running, opening browser..."
else
    # Start server in background
    python3 server.py > /tmp/forge-ai.log 2>&1 &
    SERVER_PID=$!
    
    # Wait for server to start
    sleep 3
fi

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:5000"
elif command -v firefox &> /dev/null; then
    firefox "http://localhost:5000"
elif command -v chromium &> /dev/null; then
    chromium "http://localhost:5000"
elif command -v google-chrome &> /dev/null; then
    google-chrome "http://localhost:5000"
else
    echo "Please open http://localhost:5000 in your browser"
fi

# Keep script running
wait
EOF
    
    chmod +x "$APP_DIR/AppRun"
    print_status "Launcher script created"
}

# Create desktop file
create_desktop_file() {
    print_info "Creating desktop file..."
    
    cat > "$APP_DIR/usr/share/applications/$APP_NAME.desktop" << EOF
[Desktop Entry]
Type=Application
Name=THE FORGE AI
Comment=ChatGPT 2.0 Style Interface with 575+ Capabilities
Exec=AppRun
Icon=$APP_NAME
Categories=Development;Utility;Education;
Terminal=false
StartupWMClass=$APP_NAME
EOF
    
    # Copy to root for AppImage
    cp "$APP_DIR/usr/share/applications/$APP_NAME.desktop" "$APP_DIR/"
    
    print_status "Desktop file created"
}

# Create icon
create_icon() {
    print_info "Creating application icon..."
    
    # Create a simple SVG icon (you can replace with actual icon)
    cat > "$APP_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.svg" << 'EOF'
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="32" fill="#10a37f"/>
  <text x="128" y="160" font-size="120" text-anchor="middle" fill="white">🔥</text>
</svg>
EOF
    
    # Copy to root for AppImage
    cp "$APP_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.svg" "$APP_DIR/$APP_NAME.svg"
    
    print_status "Icon created"
}

# Create AppStream metadata
create_metadata() {
    print_info "Creating AppStream metadata..."
    
    cat > "$APP_DIR/usr/share/metainfo/$APP_NAME.appdata.xml" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>$APP_NAME</id>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <name>THE FORGE AI</name>
  <summary>ChatGPT 2.0 Style Interface with 575+ Capabilities</summary>
  <description>
    <p>
      THE FORGE AI is a powerful ChatGPT 2.0 style interface with over 575 capabilities including:
    </p>
    <ul>
      <li>Programming in 20+ languages</li>
      <li>Content creation and book writing</li>
      <li>Multimedia editing and processing</li>
      <li>Code analysis and review</li>
      <li>Multiple LLM support (Kimi K2, GPT-4, Claude, Local)</li>
      <li>Offline mode with local models</li>
    </ul>
  </description>
  <launchable type="desktop-id">$APP_NAME.desktop</launchable>
  <url type="homepage">https://github.com/SpidermanTotro/Kimi-K2</url>
  <screenshots>
    <screenshot type="default">
      <caption>Main Interface</caption>
    </screenshot>
  </screenshots>
  <releases>
    <release version="$APP_VERSION" date="$(date +%Y-%m-%d)">
      <description>
        <p>Initial release with ChatGPT 2.0 style interface</p>
      </description>
    </release>
  </releases>
</component>
EOF
    
    print_status "Metadata created"
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Create virtual environment in AppDir
    python3 -m venv "$APP_DIR/usr/venv"
    source "$APP_DIR/usr/venv/bin/activate"
    
    # Install dependencies
    pip install --quiet flask flask-cors flask-socketio python-socketio pyjwt
    
    deactivate
    
    print_status "Dependencies installed"
}

# Build AppImage
build_appimage() {
    print_info "Building AppImage..."
    
    # Set architecture
    export ARCH=x86_64
    
    # Build AppImage
    ./appimagetool-x86_64.AppImage "$APP_DIR" "$APP_NAME-$APP_VERSION-$ARCH.AppImage"
    
    if [ -f "$APP_NAME-$APP_VERSION-$ARCH.AppImage" ]; then
        chmod +x "$APP_NAME-$APP_VERSION-$ARCH.AppImage"
        print_status "AppImage built successfully!"
        echo ""
        echo "Output: $APP_NAME-$APP_VERSION-$ARCH.AppImage"
        echo "Size: $(du -h "$APP_NAME-$APP_VERSION-$ARCH.AppImage" | cut -f1)"
    else
        print_error "Failed to build AppImage"
        exit 1
    fi
}

# Main execution
main() {
    check_dependencies
    download_tools
    create_appdir
    copy_files
    create_launcher
    create_desktop_file
    create_icon
    create_metadata
    install_dependencies
    build_appimage
    
    echo ""
    echo "=================================="
    echo -e "${GREEN}✓ Build complete!${NC}"
    echo "=================================="
    echo ""
    echo "To run: ./$APP_NAME-$APP_VERSION-x86_64.AppImage"
    echo ""
}

# Run main
main