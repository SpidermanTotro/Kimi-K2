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
