@echo off
REM ===================================================
REM JARVIS X AI Assistant - Environment Setup Script
REM Sets up the Python environment and installs deps
REM ===================================================

echo.
echo ==================================================
echo   JARVIS X AI Assistant - Setup Wizard
echo ==================================================
echo.

REM Check Python
echo [1/4] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.12+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Create virtual environment
echo.
echo [2/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo [4/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo WARNING: Some packages failed to install.
    echo This is usually due to missing system dependencies.
    echo.
    echo Common fixes:
    echo   - PyAudio: Install Visual C++ Build Tools
    echo   - face-recognition: Install CMake and dlib
    echo   - pycaw: Windows only
    echo.
    echo JARVIS X will still work with available features.
)

echo.
echo ==================================================
echo   Setup Complete!
echo ==================================================
echo.
echo To run JARVIS X:
echo   1. Activate the virtual environment:
echo      venv\Scripts\activate.bat
echo.
echo   2. Set your API keys (optional):
echo      set OPENAI_API_KEY=your-key-here
echo      set WEATHER_API_KEY=your-key-here
echo      set NEWS_API_KEY=your-key-here
echo.
echo   3. Launch JARVIS X:
echo      python main.py
echo.
echo   Or skip face login:
echo      python main.py --skip-login
echo.
echo   Register a face:
echo      python main.py --register-face
echo.
echo   CLI mode (no GUI):
echo      python main.py --no-gui
echo.

pause
