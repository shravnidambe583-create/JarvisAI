# 🤖 JARVIS X AI Assistant

**Just A Rather Very Intelligent System (X Edition)** — A professional, futuristic desktop AI assistant built with Python and PyQt6.

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue)
![PyQt6](https://img.shields.io/badge/UI-PyQt6-cyan)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-orange)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎤 **Voice Assistant** | Continuous listening with wake words ("Hey Jarvis") and high-quality voice synthesis (via `edge-tts` or `pyttsx3`). |
| 🌀 **Futuristic UI** | Circular animated AI core (Arc Reactor), voice waves, and drifting starfield backgrounds. |
| 🧠 **AI Brain** | OpenAI GPT integration, local offline Ollama models, and a rules-based NLP agent. |
| 🛡️ **Biometric Security** | Face recognition login (dlib-free OpenCV implementation) with intruder detection snapshots. |
| 💻 **Hardware Automation** | Complete control of system volume, screen brightness, screen locks, and system restarts/shutdowns. |
| 🔑 **Crypto Vault** | Encrypted SQLite storage (AES-128/256 standard) for passwords, secrets, and secure notes. |
| 🎯 **Missions Checklist** | Organize complex goals, set milestones, track deadlines, and monitor real-time completion progress. |
| 🔌 **Plugin Marketplace** | Dynamic plugin loader executing `.py` scripts to extend voice commands. |
| 📊 **System Monitor** | Live circular gauges displaying CPU, RAM, Disk, and Battery diagnostics. |
| 💻 **Code Execution** | Sandboxed Python compiler evaluating expressions safely from voice/text prompts. |

---

## 📁 Project Structure

```
JarvisAI/
├── main.py                     # Main application entry point (PyQt6-driven)
├── config.py                   # Central configurations & system theme definitions
├── requirements.txt            # Package dependencies
├── setup.bat                   # Auto setup script
├── build.bat                   # Standalone PyInstaller builder
├── README.md                   # This file
│
├── ui/                         # User Interface layers
│   ├── dashboard.py            # Main holographic dashboard
│   ├── style.py                # Futuristic dark-glass stylesheets (QSS)
│   └── widgets/
│       ├── arc_reactor.py      # Animated AI core status indicator (QPainter)
│       ├── waveform.py         # Dynamic voice frequency waves
│       ├── particle_bg.py      # Space starfield grid simulation
│       ├── typewriter.py       # Scrolling dialogue with typing effects
│       └── stats_panel.py      # CPU, RAM, Disk, Battery circular meters
│
├── core/                       # Brain orchestrators
│   ├── orchestrator.py         # Multi-threaded event hub & command router
│   ├── ai_chat.py              # LLM integration (OpenAI + Ollama + Fallback)
│   ├── learning.py             # Statistical command prediction & user habits
│   └── mission.py              # Mission creation and tracking system
│
├── voice/                      # Audio signal processors
│   ├── tts.py                  # edge-tts + pyttsx3 fallback
│   ├── stt.py                  # Background speech transcription thread
│   └── wakeword.py             # Wake word detector
│
├── memory/                     # Local data banks
│   ├── db_manager.py           # Thread-safe SQLite transactions
│   └── vault.py                # Cryptographic symmetric secret manager
│
├── vision/                     # OpenCV video diagnostics
│   ├── face_auth.py            # Security face login
│   ├── detector.py             # Face/Object detections & emotion recognitions
│   └── screen_intel.py         # Screenshots, OCR, and screen explainers
│
└── plugins/                    # Custom triggers Marketplace
    ├── manager.py              # Dynamic plugin loader
    └── example_plugin.py       # Simulated coin flipper & disk diagnostics plugin
```

---

## 🚀 Quick Start

### Step 1: Install Python 3.12+
Download and install from [python.org](https://www.python.org/downloads/). Ensure "Add Python to PATH" is checked during installation.

### Step 2: Clone & Setup Environment
Open terminal inside the project folder and run setup script:
```bash
# Windows
setup.bat

# Or manually:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Configure Environment Keys (Optional)
Configure API keys as environment variables:
```bash
set OPENAI_API_KEY=sk-your-openai-api-key
set WEATHER_API_KEY=your-open-weather-key
```

### Step 4: Launch JARVIS X
```bash
# Standard Launch (Webcam Scan login)
python main.py

# Skip Security Scan
python main.py --skip-login

# Register User Face Profile
python main.py --register-face

# Offline CLI mode (Terminal prompt only)
python main.py --no-gui
```

---

## 🎮 Usage Guide

| Voice / Text Command | System Action |
|----------------------|---------------|
| `"Open [chrome/vscode/notepad]"` | Launches standard desktop applications. |
| `"Close [chrome/vscode]"` | Force terminates app processes. |
| `"Set volume to [0-100]"` | Directly adjusts OS master volume. |
| `"Set brightness to [0-100]"` | Adjusts monitor display brightness. |
| `"Lock Screen" / "Sleep computer"` | Locks desktop or puts the computer in sleep state. |
| `"Screenshot" / "Explain my screen"`| Takes screenshot and runs GPT-4o-vision/local analysis. |
| `"Create mission [name]"` | Registers a new milestone project tracker. |
| `"Add task [desc] to mission [name]"` | Appends checklist tasks to the mission. |
| `"Complete task [ID]"` | Marks task finished and increments progress gauge. |
| `"Save password [label] value [secret]"` | Encrypts and locks secret in the Crypto Vault. |
| `"Retrieve password [label]"` | Decrypts and outputs secret value in the console. |
| `"Execute python [code]"` | Compiles and executes code block safely inside sandbox. |
| `"Emergency"` / `"Panic Alert"` | Dispatches automated notifications to trusted contacts. |
| `"Set persona [stark/military/scientific]"` | Alters conversational tone and vocabulary. |

---

## 🏗️ Standalone Packaging

To bundle JARVIS X into a single Windows executable:
```bash
build.bat
```
The resulting executable will be saved inside the `dist/` directory.

---

## 🧪 Unit Testing

To run verification test suites validating database operations, cryptos, and command sandboxes:
```bash
# Database & Vault tests
python -m unittest tests/test_db.py

# Core logic & Command routing tests
python -m unittest tests/test_core.py
```
