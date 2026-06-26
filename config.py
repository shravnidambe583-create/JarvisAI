"""
JARVIS X AI Assistant - Configuration Module
===========================================
Central configuration file for all JARVIS X settings.
Contains API keys, paths, wake words, and default values.
"""

import os
import platform

# ──────────────────────────────────────────────
# General Settings
# ──────────────────────────────────────────────
APP_NAME = "JARVIS X"
APP_VERSION = "2.1.0"
APP_AUTHOR = "JARVIS Dev Team"
PYTHON_VERSION = "3.12"

# Base directory (root of the project)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Asset and database paths
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATABASE_DIR = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "history.db")

# Ensure directories exist
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# API Keys (User should set these via env vars)
# ──────────────────────────────────────────────
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
PIVOTECH_ACCESS_KEY = os.environ.get("PV_ACCESS_KEY", "")  # Picovoice Porcupine

# ──────────────────────────────────────────────
# OpenAI / Ollama Settings
# ──────────────────────────────────────────────
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 1024
OPENAI_TEMPERATURE = 0.7

# Ollama offline AI settings
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"
OFFLINE_MODE = False  # Auto-switches to True if no internet

# ──────────────────────────────────────────────
# Voice Settings
# ──────────────────────────────────────────────
WAKE_WORDS = ["hey jarvis", "jarvis"]
TTS_RATE = 180          # Words per minute
TTS_VOLUME = 1.0        # 0.0 to 1.0
TTS_VOICE_INDEX = 0     # 0 = male, 1 = female (system dependent)

# Speech recognition settings
RECOGNIZER_ENERGY_THRESHOLD = 300
RECOGNIZER_DYNAMIC_ENERGY = True
RECOGNIZER_PAUSE_THRESHOLD = 0.8
MICROPHONE_DEVICE_INDEX = None  # None = default mic

# ──────────────────────────────────────────────
# Face Recognition Settings
# ──────────────────────────────────────────────
FACE_RECOGNITION_ENABLED = True
FACE_RECOGNITION_TOLERANCE = 0.6
FACE_DATA_DIR = os.path.join(ASSETS_DIR, "face_data")
os.makedirs(FACE_DATA_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# System Monitoring
# ──────────────────────────────────────────────
SYSTEM_MONITOR_INTERVAL = 5  # seconds between updates

# ──────────────────────────────────────────────
# Screenshot Settings
# ──────────────────────────────────────────────
SCREENSHOT_DIR = os.path.join(BASE_DIR, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ──────────────────────────────────────────────
# Default User Location
# ──────────────────────────────────────────────
DEFAULT_CITY = "New Delhi"
DEFAULT_COUNTRY = "India"

# ──────────────────────────────────────────────
# Application Paths (Windows-specific)
# ──────────────────────────────────────────────
if platform.system() == "Windows":
    APP_PATHS = {
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "chrome_alt": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "vscode": r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
        "taskmgr": "taskmgr.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
    }
else:
    APP_PATHS = {
        "chrome": "google-chrome",
        "vscode": "code",
        "notepad": "gedit",
        "calculator": "gnome-calculator",
        "explorer": "nautilus",
        "taskmgr": "gnome-system-monitor",
        "cmd": "xterm",
        "powershell": "pwsh",
    }
