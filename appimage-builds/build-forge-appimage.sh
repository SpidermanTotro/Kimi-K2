#!/bin/bash
# THE FORGE AI - Real Working AppImage Builder
# Creates a fully functional Linux desktop application

set -e

echo "🔥 THE FORGE AI - AppImage Builder"
echo "===================================="
echo ""

# Configuration
APP_NAME="TheForgeAI"
APP_VERSION="2.0.0"
APP_DIR="TheForgeAI.AppDir"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Download AppImage tools
download_tools() {
    print_info "Downloading AppImage tools..."
    
    if [ ! -f "appimagetool-x86_64.AppImage" ]; then
        wget -q --show-progress https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
        chmod +x appimagetool-x86_64.AppImage
        print_status "Downloaded appimagetool"
    else
        print_status "appimagetool already exists"
    fi
}

# Create AppDir structure
create_appdir() {
    print_info "Creating AppDir structure..."
    
    rm -rf "$APP_DIR"
    mkdir -p "$APP_DIR"
    mkdir -p "$APP_DIR/usr/bin"
    mkdir -p "$APP_DIR/usr/lib"
    mkdir -p "$APP_DIR/usr/share/applications"
    mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"
    
    print_status "AppDir structure created"
}

# Copy application files
copy_files() {
    print_info "Copying application files..."
    
    # Copy web interface
    cp -r ../web_interface "$APP_DIR/usr/bin/"
    
    # Copy Python files
    cp ../forge_server.py "$APP_DIR/usr/bin/"
    cp ../forge_cli.py "$APP_DIR/usr/bin/"
    cp ../forge_implementation.py "$APP_DIR/usr/bin/"
    
    # Copy live programs
    cp -r ../live_programs "$APP_DIR/usr/bin/"
    
    # Copy requirements
    cp ../requirements.txt "$APP_DIR/usr/bin/"
    
    print_status "Application files copied"
}

# Create launcher script
create_launcher() {
    print_info "Creating launcher script..."
    
    cat > "$APP_DIR/AppRun" << 'LAUNCHER_EOF'
#!/bin/bash
# THE FORGE AI Launcher

APPDIR="$(dirname "$(readlink -f "$0")")"
export PYTHONPATH="$APPDIR/usr/bin:$PYTHONPATH"

cd "$APPDIR/usr/bin/web_interface"

# Check if server is running
if pgrep -f "python.*server.py" > /dev/null; then
    echo "Server already running"
else
    # Start server
    python3 server.py > /tmp/forge-ai.log 2>&1 &
    sleep 2
fi

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:9001"
elif command -v firefox &> /dev/null; then
    firefox "http://localhost:9001"
else
    echo "Open http://localhost:9001 in your browser"
fi

wait
LAUNCHER_EOF
    
    chmod +x "$APP_DIR/AppRun"
    print_status "Launcher created"
}

# Create desktop file
create_desktop_file() {
    print_info "Creating desktop file..."
    
    cat > "$APP_DIR/$APP_NAME.desktop" << EOF
[Desktop Entry]
Type=Application
Name=THE FORGE AI
Comment=ChatGPT 2.0 Style Interface
Exec=AppRun
Icon=$APP_NAME
Categories=Development;Utility;
Terminal=false
EOF
    
    print_status "Desktop file created"
}

# Create icon
create_icon() {
    print_info "Creating icon..."
    
    cat > "$APP_DIR/$APP_NAME.png" << 'EOF'
iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAA
EOF
    
    # Create simple SVG icon instead
    cat > "$APP_DIR/$APP_NAME.svg" << 'EOF'
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="32" fill="#10a37f"/>
  <text x="128" y="160" font-size="120" text-anchor="middle" fill="white">🔥</text>
</svg>
EOF
    
    print_status "Icon created"
}

# Build AppImage
build_appimage() {
    print_info "Building AppImage..."
    
    export ARCH=x86_64
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

# Main
main() {
    download_tools
    create_appdir
    copy_files
    create_launcher
    create_desktop_file
    create_icon
    build_appimage
    
    echo ""
    echo "===================================="
    echo -e "${GREEN}✓ Build complete!${NC}"
    echo "===================================="
    echo ""
    echo "To run: ./$APP_NAME-$APP_VERSION-x86_64.AppImage"
    echo ""
}

main