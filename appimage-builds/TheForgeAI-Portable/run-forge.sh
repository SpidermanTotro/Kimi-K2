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
