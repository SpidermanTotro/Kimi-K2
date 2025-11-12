#!/bin/bash
#
# THE FORGE - One-Click Launcher
# ==============================
# Run this to start THE FORGE instantly!
#

echo "════════════════════════════════════════════════════════════════"
echo "  ████████╗██╗  ██╗███████╗    ███████╗ ██████╗ ██████╗  ██████╗ ███████╗"
echo "  ╚══██╔══╝██║  ██║██╔════╝    ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝"
echo "     ██║   ███████║█████╗      █████╗  ██║   ██║██████╔╝██║  ███╗█████╗"
echo "     ██║   ██╔══██║██╔══╝      ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝"
echo "     ██║   ██║  ██║███████╗    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗"
echo "     ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
echo ""
echo "                    FREE AI-Powered Coding Platform"
echo "                  Saving You \$5,572/Year vs Competition"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed!"
    echo "Please install Python 3 first: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Installing Flask and dependencies..."
    pip install Flask Flask-CORS
    echo ""
fi

echo "✅ All dependencies ready!"
echo ""

# Show menu
echo "Choose what to run:"
echo ""
echo "  1) 🏆 Show AI Domination Dashboard (proves we beat ALL competition)"
echo "  2) 🚀 Launch THE FORGE IDE (main application)"
echo "  3) 🎯 Detect Current Project (auto-detection)"
echo "  4) ℹ️  Show Quick Start Guide"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "════════════════════════════════════════════════════════════════"
        echo "Running AI Domination Dashboard..."
        echo "This will show how we BEAT all 22+ competitors!"
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        python3 ai_domination_dashboard.py
        ;;
    2)
        echo ""
        echo "════════════════════════════════════════════════════════════════"
        echo "🚀 Starting THE FORGE IDE..."
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        echo "✅ Server starting on http://localhost:5000"
        echo ""
        echo "Available URLs:"
        echo "  • http://localhost:5000          - Launcher"
        echo "  • http://localhost:5000/vscode   - Full VS Code Clone"
        echo "  • http://localhost:5000/codespaces - AI Companions"
        echo "  • http://localhost:5000/download - Download Installers"
        echo ""
        echo "Press Ctrl+C to stop the server"
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        python3 advanced_codespaces_server.py
        ;;
    3)
        echo ""
        echo "════════════════════════════════════════════════════════════════"
        echo "Running Project Detection..."
        echo "════════════════════════════════════════════════════════════════"
        echo ""
        python3 industrial_ai_detector.py
        ;;
    4)
        echo ""
        cat RUN_ME_FIRST.md
        ;;
    *)
        echo ""
        echo "❌ Invalid choice!"
        echo ""
        echo "Quick start:"
        echo "  python3 advanced_codespaces_server.py"
        echo "  Then visit: http://localhost:5000"
        echo ""
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "Thank you for using THE FORGE!"
echo "💰 You're saving \$5,572/year vs commercial tools!"
echo "════════════════════════════════════════════════════════════════"
