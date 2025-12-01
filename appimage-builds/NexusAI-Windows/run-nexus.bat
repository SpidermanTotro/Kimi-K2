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
