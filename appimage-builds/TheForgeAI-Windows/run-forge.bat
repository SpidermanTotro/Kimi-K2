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
