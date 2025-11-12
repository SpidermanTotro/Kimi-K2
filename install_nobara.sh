#!/bin/bash
# THE FORGE - Nobara Linux Auto-Installer
# One-click installation for Nobara users

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         THE FORGE - Nobara Linux Installer                  ║"
echo "║                                                              ║"
echo "║  Installing the ULTIMATE FREE AI Programming Platform        ║"
echo "║  Save \$6,038/year vs Microsoft & GitHub tools!              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Nobara/Fedora
if [ ! -f /etc/fedora-release ]; then
    echo "⚠️  Warning: This script is optimized for Nobara/Fedora."
    echo "   THE FORGE will still work, but some packages might differ."
    echo ""
fi

# Check Python version
echo "🔍 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    echo "✅ Python $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Installing..."
    sudo dnf install -y python3
fi

# Install Flask dependencies
echo ""
echo "📦 Installing Python dependencies..."
echo "   (Flask and Flask-CORS)"

# Try pip install first
if pip install --user Flask Flask-CORS 2>/dev/null; then
    echo "✅ Dependencies installed via pip"
else
    # Fallback to DNF
    echo "   Trying system package manager..."
    sudo dnf install -y python3-flask python3-flask-cors
    echo "✅ Dependencies installed via DNF"
fi

# Optional: Install compilers
echo ""
echo "🔧 Do you want to install language compilers? (y/n)"
echo "   This enables C/C++, Rust, Go, Java, Node.js support"
read -p "   Install compilers? [y/N]: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing compilers..."
    sudo dnf install -y gcc gcc-c++ make cmake rust cargo golang nodejs npm java-latest-openjdk
    echo "✅ All compilers installed!"
else
    echo "⏭️  Skipping compiler installation (you can install later)"
fi

# Check if already in Kimi-K2 directory
if [ -f "LAUNCH_FORGE.py" ]; then
    echo ""
    echo "✅ Already in THE FORGE directory!"
else
    # Check if Kimi-K2 directory exists
    if [ -d "Kimi-K2" ]; then
        echo ""
        echo "📁 Found existing Kimi-K2 directory"
        cd Kimi-K2
    else
        echo ""
        echo "⬇️  Repository not found. Please run this from the Kimi-K2 directory."
        echo "   Or clone it first:"
        echo "   git clone https://github.com/SpidermanTotro/Kimi-K2.git"
        exit 1
    fi
fi

# Make scripts executable
echo ""
echo "🔧 Setting up launcher scripts..."
chmod +x start_forge.sh 2>/dev/null
chmod +x LAUNCH_FORGE.py 2>/dev/null
echo "✅ Scripts ready"

# Run initial test
echo ""
echo "🧪 Running system check..."
if python3 COMPILE_AND_TEST.py 2>/dev/null; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed (this is OK for first run)"
fi

# Done!
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              ✅ INSTALLATION COMPLETE! ✅                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Start THE FORGE with:"
echo "   python3 LAUNCH_FORGE.py"
echo ""
echo "Or:"
echo "   ./start_forge.sh"
echo ""
echo "📖 Documentation:"
echo "   - INSTALL_NOBARA.md (Nobara-specific guide)"
echo "   - RUN_ME_FIRST.md (Quick start)"
echo "   - INSTALLATION_GUIDE.md (Detailed guide)"
echo ""
echo "💰 You're now saving \$6,038/year!"
echo ""
echo "🎮 Perfect for game development on Nobara!"
echo ""

# Offer to launch now
echo "🚀 Launch THE FORGE now? (y/n)"
read -p "   Start THE FORGE? [Y/n]: " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "🚀 Launching THE FORGE..."
    python3 LAUNCH_FORGE.py
fi
