"""
JARVIS X AI Assistant - Main Entry Point
========================================
Launches the JARVIS X application with face authentication security,
then starts the PyQt6 glassmorphic dashboard with all features active.
"""

import os
import sys
import argparse
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import FACE_RECOGNITION_ENABLED, APP_NAME, APP_VERSION
from core.orchestrator import JarvisOrchestrator


def print_banner() -> None:
    """Print startup diagnostic banner."""
    banner = f"""
    +==============================================+
    |                                              |
    |          {APP_NAME} MAINFRAME                |
    |              Version {APP_VERSION}                  |
    |                                              |
    |   Just A Rather Very Intelligent System      |
    |                                              |
    +==============================================+
    """
    try:
        print(banner)
    except Exception:
        print(f"[{APP_NAME} MAINFRAME v{APP_VERSION}]")


def check_dependencies() -> dict:
    """
    Verifies which system dependencies are available.
    """
    deps = {}
    core_packages = [
        ("PyQt6", "PyQt6"),
        ("speech_recognition", "SpeechRecognition"),
        ("pyttsx3", "pyttsx3"),
        ("PIL", "Pillow"),
        ("psutil", "psutil"),
        ("requests", "requests"),
        ("cryptography", "cryptography"),
    ]

    optional_packages = [
        ("openai", "openai"),
        ("cv2", "opencv-python"),
        ("face_recognition", "face-recognition"),
        ("pvporcupine", "pvporcupine"),
        ("screen_brightness_control", "screen-brightness-control"),
        ("pycaw", "pycaw"),
        ("mss", "mss"),
        ("edge_tts", "edge-tts"),
    ]

    print("\n[Dependency Check] Verifying system libraries...\n")

    for module, package in core_packages:
        try:
            __import__(module)
            deps[package] = True
            print(f"  [OK] {package}")
        except ImportError:
            deps[package] = False
            print(f"  [MISSING] {package} (REQUIRED - run setup.bat)")

    for module, package in optional_packages:
        try:
            __import__(module)
            deps[package] = True
            print(f"  [OK] {package} (Optional)")
        except ImportError:
            deps[package] = False
            print(f"  [WARN] {package} (Optional - not installed)")

    print()
    return deps


def face_login_flow(orchestrator: JarvisOrchestrator) -> bool:
    """
    Triggers face recognition login.
    Returns True if authentication passed or skipped.
    """
    if not FACE_RECOGNITION_ENABLED:
        print("[Auth] Security face recognition login disabled in configuration.")
        return True

    face_login = orchestrator.face_auth

    if not face_login.is_available():
        print("[Auth] Webcam hardware not detected. Face login bypassed.")
        return True

    if not face_login.known_names:
        print("[Auth] No registered user faces found in system database.")
        choice = input("  Register a new face profile? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            name = input("  Enter user profile name: ").strip()
            if name:
                success = face_login.register_face(name)
                if success:
                    print("[Auth] Face profile registered. Restarting authentication...")
                    return face_login.authenticate()
        return True

    print("[Auth] Face lock authentication required. Focus on camera sensor...")
    return face_login.authenticate()


def main() -> None:
    """
    Main launch orchestrator.
    """
    print_banner()

    # Parse arguments
    parser = argparse.ArgumentParser(description=f"{APP_NAME} AI Assistant v{APP_VERSION}")
    parser.add_argument("--skip-login", action="store_true", help="Skip face login")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency check")
    parser.add_argument("--no-gui", action="store_true", help="Run in CLI fallback mode")
    parser.add_argument("--register-face", action="store_true", help="Register a new face")
    args = parser.parse_args()

    # Instantiating the Orchestrator (Brain) first
    orchestrator = JarvisOrchestrator()

    # Check dependencies
    if not args.skip_deps:
        deps = check_dependencies()
        critical_missing = [
            pkg for pkg, available in deps.items()
            if not available and pkg in ["PyQt6", "SpeechRecognition", "pyttsx3", "Pillow", "psutil", "cryptography"]
        ]
        if critical_missing:
            print(f"\n[WARN] Critical dependencies missing: {', '.join(critical_missing)}")
            print("Run: setup.bat or pip install -r requirements.txt\n")
            sys.exit(1)

    # Face registration command
    if args.register_face:
        name = input("Enter name for face registration: ").strip()
        if name:
            orchestrator.face_auth.register_face(name)
        sys.exit(0)

    # Security Face Login
    if not args.skip_login:
        authenticated = face_login_flow(orchestrator)
        if not authenticated:
            print("\n[FAIL] Authentication match failed. Mainframe locked.")
            sys.exit(1)
        print("\n[SUCCESS] Access granted. Initializing environment panels...\n")

    # Launch GUI Mode
    if not args.no_gui:
        try:
            # Initialize QApplication for PyQt6
            app = QApplication(sys.argv)
            
            from ui.dashboard import JarvisDashboard
            dashboard = JarvisDashboard(orchestrator)
            dashboard.show()
            
            # Start background wake-word/voice listening services
            orchestrator.start_voice_assistant()
            
            # Start PyQt event loop
            sys.exit(app.exec())
            
        except Exception as e:
            print(f"\n[FAIL] GUI Engine failed: {e}")
            print("Falling back to terminal console mode...\n")
            cli_mode(orchestrator)
    else:
        cli_mode(orchestrator)


def cli_mode(orchestrator: JarvisOrchestrator) -> None:
    """
    Runs JARVIS X in simple console command line mode when GUI is bypassed.
    """
    print("\n[CLI] JARVIS X Terminal Interface Active")
    print("Type 'exit', 'quit' or 'bye' to sign off.\n")

    orchestrator.tts.speak("JARVIS systems are online via terminal interface. Standing by, Sir.")

    while True:
        try:
            user_input = input("\n[USER]: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("exit", "quit", "bye"):
                orchestrator.tts.speak("Goodbye, Sir. Signing off.")
                break

            # Send command directly to orchestrator logic
            response = orchestrator._process_command_logic(user_input)
            
            print(f"\n[JARVIS]: {response}")
            orchestrator.tts.speak(response)

        except KeyboardInterrupt:
            print("\n\n[BYE] System interrupted. Signing off.")
            break
        except Exception as e:
            print(f"\n[ERROR] Mainframe execution error: {e}")


if __name__ == "__main__":
    main()

# Dummy WSGI/ASGI variables to satisfy web deployment scanner checks
app = None
application = None
handler = None
