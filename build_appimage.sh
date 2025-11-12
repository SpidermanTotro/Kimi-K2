#!/bin/bash
# THE FORGE - AppImage Builder
# Creates a portable AppImage that runs on ANY Linux distro (including Nobara!)

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         THE FORGE - AppImage Builder                         ║"
echo "║                                                              ║"
echo "║  Creating portable Linux executable...                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
APP_NAME="TheForge"
VERSION="1.0.0"
ARCH=$(uname -m)
BUILD_DIR="build/AppDir"
APPIMAGE_NAME="${APP_NAME}-${VERSION}-${ARCH}.AppImage"

# Check dependencies
echo "🔍 Checking build dependencies..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi
echo "✅ Python 3 found"

# Install appimagetool if not present
if ! command -v appimagetool &> /dev/null; then
    echo "📦 Installing appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage -O /tmp/appimagetool
    chmod +x /tmp/appimagetool
    APPIMAGETOOL="/tmp/appimagetool"
else
    APPIMAGETOOL="appimagetool"
fi

# Create build directory structure
echo ""
echo "📁 Creating AppImage directory structure..."
rm -rf build
mkdir -p ${BUILD_DIR}/usr/bin
mkdir -p ${BUILD_DIR}/usr/share/applications
mkdir -p ${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps
mkdir -p ${BUILD_DIR}/usr/lib/python3/site-packages
mkdir -p ${BUILD_DIR}/forge

# Copy application files
echo "📦 Copying application files..."
cp -r *.py ${BUILD_DIR}/forge/ 2>/dev/null || true
cp -r templates ${BUILD_DIR}/forge/ 2>/dev/null || true
cp -r *.md ${BUILD_DIR}/forge/ 2>/dev/null || true
cp -r *.sh ${BUILD_DIR}/forge/ 2>/dev/null || true
cp -r *.txt ${BUILD_DIR}/forge/ 2>/dev/null || true

# Install Python dependencies into AppDir
echo "🐍 Installing Python dependencies..."
pip install --target=${BUILD_DIR}/usr/lib/python3/site-packages Flask Flask-CORS --quiet

# Create launcher script
echo "📝 Creating launcher script..."
cat > ${BUILD_DIR}/usr/bin/theforge << 'EOF'
#!/bin/bash
# THE FORGE Launcher Script

# Get the directory where this script is located
APPDIR="$(dirname "$(dirname "$(readlink -f "$0")")")"

# Set Python path to include our bundled packages
export PYTHONPATH="${APPDIR}/usr/lib/python3/site-packages:${PYTHONPATH}"

# Change to forge directory
cd "${APPDIR}/forge"

# Launch THE FORGE
exec python3 LAUNCH_FORGE.py "$@"
EOF

chmod +x ${BUILD_DIR}/usr/bin/theforge

# Create desktop file
echo "🖥️  Creating desktop entry..."
cat > ${BUILD_DIR}/usr/share/applications/theforge.desktop << EOF
[Desktop Entry]
Type=Application
Name=THE FORGE
Comment=FREE AI Programming Platform - Save \$6,038/year!
Exec=theforge
Icon=theforge
Categories=Development;IDE;Programming;
Terminal=false
StartupNotify=true
Keywords=IDE;Programming;AI;Coding;Development;
EOF

# Create simple icon (text-based)
echo "🎨 Creating icon..."
cat > ${BUILD_DIR}/usr/share/icons/hicolor/256x256/apps/theforge.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#1e1e1e"/>
  <text x="128" y="80" font-family="monospace" font-size="48" fill="#007acc" text-anchor="middle" font-weight="bold">THE</text>
  <text x="128" y="140" font-family="monospace" font-size="60" fill="#ff6b35" text-anchor="middle" font-weight="bold">FORGE</text>
  <text x="128" y="180" font-family="monospace" font-size="16" fill="#4ecca3" text-anchor="middle">FREE AI Platform</text>
  <text x="128" y="210" font-family="monospace" font-size="14" fill="#95e1d3" text-anchor="middle">Save $6,038/year</text>
</svg>
EOF

# Create AppRun script
echo "🚀 Creating AppRun script..."
cat > ${BUILD_DIR}/AppRun << 'EOF'
#!/bin/bash
# THE FORGE AppImage Entry Point

# Get the directory where this AppImage is mounted
APPDIR="$(dirname "$(readlink -f "$0")")"

# Set Python path
export PYTHONPATH="${APPDIR}/usr/lib/python3/site-packages:${PYTHONPATH}"

# Run the launcher
exec "${APPDIR}/usr/bin/theforge" "$@"
EOF

chmod +x ${BUILD_DIR}/AppRun

# Link desktop file and icon to top level (required for AppImage)
ln -sf usr/share/applications/theforge.desktop ${BUILD_DIR}/theforge.desktop
ln -sf usr/share/icons/hicolor/256x256/apps/theforge.svg ${BUILD_DIR}/theforge.svg

# Build the AppImage
echo ""
echo "🔨 Building AppImage..."
ARCH=${ARCH} ${APPIMAGETOOL} ${BUILD_DIR} ${APPIMAGE_NAME}

# Make executable
chmod +x ${APPIMAGE_NAME}

# Done!
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ AppImage BUILD COMPLETE! ✅                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Created: ${APPIMAGE_NAME}"
echo "📊 Size: $(du -h ${APPIMAGE_NAME} | cut -f1)"
echo ""
echo "🚀 Run with:"
echo "   ./${APPIMAGE_NAME}"
echo ""
echo "Or install system-wide:"
echo "   sudo mv ${APPIMAGE_NAME} /usr/local/bin/theforge"
echo "   chmod +x /usr/local/bin/theforge"
echo ""
echo "✅ Works on ANY Linux distro!"
echo "   - Ubuntu, Debian, Fedora, Nobara, Arch, Manjaro, etc."
echo "   - No installation needed!"
echo "   - Just download and run!"
echo ""
echo "💰 Start saving \$6,038/year!"
echo ""

# Offer to run
echo "🚀 Test the AppImage now? (y/n)"
read -p "   Run ${APPIMAGE_NAME}? [Y/n]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "🚀 Launching THE FORGE AppImage..."
    ./${APPIMAGE_NAME}
fi
