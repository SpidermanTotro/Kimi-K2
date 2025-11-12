#!/bin/bash
# Quick setup script for Kimi K2 Web Deployment

echo "=================================="
echo "🔥 Kimi K2 - THE FORGE AI Setup"
echo "=================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the server, run one of:"
echo ""
echo "   For REST API Server:"
echo "   python3 forge_server.py"
echo ""
echo "   For Web GUI:"
echo "   python3 forge_gui.py"
echo ""
echo "   Or use the launcher:"
echo "   python3 start_server.py          # API server"
echo "   python3 start_server.py --gui    # GUI interface"
echo ""
echo "📍 Server will be available at http://localhost:5000"
echo ""
echo "🌐 To deploy to free hosting:"
echo "   See DEPLOYMENT.md for step-by-step instructions"
echo ""
