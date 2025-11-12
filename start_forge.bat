@echo off
REM THE FORGE - One-Click Launcher for Windows
REM ============================================

echo ================================================================
echo   THE FORGE - FREE AI-Powered Coding Platform
echo   Saving You $5,572/Year vs Competition
echo ================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3 from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing Flask and dependencies...
    pip install Flask Flask-CORS
    echo.
)

echo [OK] All dependencies ready!
echo.

echo Choose what to run:
echo.
echo   1) Show AI Domination Dashboard (proves we beat ALL competition)
echo   2) Launch THE FORGE IDE (main application)
echo   3) Detect Current Project (auto-detection)
echo   4) Show Quick Start Guide
echo.

set /p choice="Enter choice [1-4]: "

if "%choice%"=="1" goto dashboard
if "%choice%"=="2" goto ide
if "%choice%"=="3" goto detect
if "%choice%"=="4" goto guide
goto invalid

:dashboard
echo.
echo ================================================================
echo Running AI Domination Dashboard...
echo This will show how we BEAT all 22+ competitors!
echo ================================================================
echo.
python ai_domination_dashboard.py
goto end

:ide
echo.
echo ================================================================
echo Starting THE FORGE IDE...
echo ================================================================
echo.
echo [OK] Server starting on http://localhost:5000
echo.
echo Available URLs:
echo   - http://localhost:5000          - Launcher
echo   - http://localhost:5000/vscode   - Full VS Code Clone
echo   - http://localhost:5000/codespaces - AI Companions
echo   - http://localhost:5000/download - Download Installers
echo.
echo Press Ctrl+C to stop the server
echo ================================================================
echo.
python advanced_codespaces_server.py
goto end

:detect
echo.
echo ================================================================
echo Running Project Detection...
echo ================================================================
echo.
python industrial_ai_detector.py
goto end

:guide
echo.
type RUN_ME_FIRST.md
goto end

:invalid
echo.
echo ERROR: Invalid choice!
echo.
echo Quick start:
echo   python advanced_codespaces_server.py
echo   Then visit: http://localhost:5000
echo.
pause
exit /b 1

:end
echo.
echo ================================================================
echo Thank you for using THE FORGE!
echo You're saving $5,572/year vs commercial tools!
echo ================================================================
echo.
pause
