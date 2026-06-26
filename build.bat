@echo off
REM ===================================================
REM JARVIS X AI Assistant - Windows Build Script
REM Creates a standalone executable using PyInstaller
REM ===================================================

echo.
echo ==================================================
echo   JARVIS X AI Assistant - Build Script
echo ==================================================
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.12+ from https://python.org
    pause
    exit /b 1
)

echo.
echo [1/3] Installing/upgrading build tools...
pip install pyinstaller

echo.
echo [2/3] Building executable with PyInstaller...
pyinstaller --noconfirm --onefile --windowed ^
    --name "JARVIS_X" ^
    --add-data "assets;assets" ^
    --add-data "database;database" ^
    --hidden-import=PyQt6 ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PIL ^
    --hidden-import=speech_recognition ^
    --hidden-import=pyttsx3 ^
    --hidden-import=edge_tts ^
    --hidden-import=psutil ^
    --hidden-import=requests ^
    --hidden-import=openai ^
    --hidden-import=cryptography ^
    --hidden-import=screen_brightness_control ^
    --icon=NONE ^
    main.py

echo.
echo [3/3] Build complete!
echo.
echo The executable can be found in the 'dist' folder.
echo.

pause
