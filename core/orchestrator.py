import os
import re
import threading
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# Database & Memory
from memory.db_manager import DatabaseManager
from memory.vault import MemoryVault

# Voice
from voice.tts import SpeakEngine
from voice.stt import VoiceListenerThread
from voice.wakeword import WakeWordDetectorThread

# Automations
from automation.system_control import SystemController
from automation.app_control import AppController
from automation.email_client import EmailClient

# Vision
from vision.face_auth import FaceLogin
from vision.detector import AIDetector
from vision.screen_intel import ScreenIntelligence

# Core AI
from core.ai_chat import AIChat
from core.learning import LearningSystem
from core.mission import MissionSystem
from plugins.manager import PluginManager

class CommandExecutorThread(QThread):
    """QThread to execute actions/commands in the background to avoid freezing the PyQt6 UI."""
    response_ready = pyqtSignal(str)
    
    def __init__(self, orchestrator, command_text):
        super().__init__()
        self.orchestrator = orchestrator
        self.command_text = command_text

    def run(self):
        # Delegate command processing to orchestrator's core routine
        response = self.orchestrator._process_command_logic(self.command_text)
        self.response_ready.emit(response)

class JarvisOrchestrator(QObject):
    """Central operations manager (brain) for JARVIS X."""
    
    # UI signals
    ui_log = pyqtSignal(str, str)             # Message content, category ('info', 'user', 'jarvis', 'success', 'warning', 'error')
    voice_state_changed = pyqtSignal(str)     # 'idle', 'listening', 'processing', 'speaking'
    system_status_updated = pyqtSignal(dict)  # CPU, RAM etc.
    command_predicted = pyqtSignal(list)       # List of command suggestions
    
    def __init__(self, db=None, vault=None):
        super().__init__()
        print("[Orchestrator] Initializing JARVIS X Core System...")
        
        # 1. Init Database and Storage
        self.db = db or DatabaseManager()
        self.vault = vault or MemoryVault()
        
        # 2. Init AI Brain
        self.ai = AIChat(self.db)
        self.learning = LearningSystem(self.db)
        self.missions = MissionSystem(self.db)
        
        # 3. Init Hardware Controllers
        self.system = SystemController()
        self.apps = AppController()
        self.email = EmailClient()
        
        # 4. Init Vision & Screen Intelligence
        self.face_auth = FaceLogin()
        self.detector = AIDetector()
        self.screen_intel = ScreenIntelligence()
        
        # 5. Init Plugin System
        self.plugins = PluginManager(self)
        self.plugins.load_plugins()
        
        # 6. Init Voice Engines
        self.tts = SpeakEngine()
        self.stt_thread = None
        self.wake_thread = None
        
        # Connect TTS signals
        self.tts.signals.started.connect(lambda: self.voice_state_changed.emit("speaking"))
        self.tts.signals.finished.connect(lambda: self.voice_state_changed.emit("idle"))
        self.tts.signals.error.connect(lambda err: self.ui_log.emit(f"TTS Error: {err}", "error"))
        
        # Setup threading locks
        self.lock = threading.Lock()
        
        # System state variables
        self.is_monitoring = False
        self.emergency_contacts = ["emergency@example.com"] # Default emergency contact

    def start_voice_assistant(self):
        """Starts the wake word detector thread in the background."""
        print("[Orchestrator] Starting voice assistant wake-word service...")
        self.wake_thread = WakeWordDetectorThread()
        self.wake_thread.wake_word_detected.connect(self.activate_listening)
        self.wake_thread.status_changed.connect(lambda status: print(f"[Wakeword Status]: {status}"))
        self.wake_thread.start()

    def activate_listening(self):
        """Triggers active STT speech listening mode (stops wakeword listening temporarily)."""
        with self.lock:
            # Stop wakeword listener if running
            if self.wake_thread and self.wake_thread.isRunning():
                self.wake_thread.stop()
                
            # Play a futuristic prompt chime
            self.tts.speak("Yes Sir. Standing by.")
            self.ui_log.emit("System listening...", "info")
            self.voice_state_changed.emit("listening")
            
            # Start speech recognizer thread
            self.stt_thread = VoiceListenerThread()
            self.stt_thread.recognized_text.connect(self.process_command)
            self.stt_thread.status_changed.connect(self._handle_stt_status)
            self.stt_thread.start()

    def _handle_stt_status(self, status):
        """Maps STT status changes to UI voice states."""
        if status == "listening":
            self.voice_state_changed.emit("listening")
        elif status == "processing":
            self.voice_state_changed.emit("processing")
        elif status == "idle":
            self.voice_state_changed.emit("idle")
            # Re-enable wake word detection if speech recognition timed out
            self.restart_wakeword_listener()

    def restart_wakeword_listener(self):
        """Transitions back to low-power background wake-word listening."""
        with self.lock:
            if self.stt_thread and self.stt_thread.isRunning():
                self.stt_thread.stop()
            if self.wake_thread and not self.wake_thread.isRunning():
                self.wake_thread.start()
            self.voice_state_changed.emit("idle")

    def process_command(self, command_text: str):
        """Dispatches voice or text command to background execution thread to keep UI fluid."""
        self.ui_log.emit(command_text, "user")
        self.voice_state_changed.emit("processing")
        
        # Log to db history
        self.db.log_command(command_text)
        
        # Start execution thread
        self.executor = CommandExecutorThread(self, command_text)
        self.executor.response_ready.connect(self._handle_executor_response)
        self.executor.start()

    def _handle_executor_response(self, response: str):
        """Speaks the response, logs to UI, and updates predictions."""
        self.ui_log.emit(response, "jarvis")
        self.voice_state_changed.emit("speaking")
        
        # Speak the response
        self.tts.speak(response)
        
        # Restart wake word listener after response is done speaking
        # (This is handled asynchronously by the QThread monitor or we can trigger it after speech finishes)
        threading.Thread(target=self._wait_for_speech_to_finish, daemon=True).start()
        
        # Update suggested predictions
        preds = self.learning.predict_next_command()
        self.command_predicted.emit(preds)

    def _wait_for_speech_to_finish(self):
        """Waits for speech output to stop, then re-enables background wake word detector."""
        import time
        while self.tts._is_speaking:
            time.sleep(0.5)
        self.restart_wakeword_listener()

    def _process_command_logic(self, query: str) -> str:
        """Core command routing & execution logic."""
        q = query.lower().strip()
        
        # 1. Check Custom Voice Shortcuts mapping
        shortcut_action = self.learning.get_shortcut_action(query)
        if shortcut_action:
            # Execute the shortcut action (app name or system command)
            if shortcut_action.endswith((".exe", ".bat", ".lnk")):
                self.apps.open_app(shortcut_action)
                return f"Executing shortcut command to launch {os.path.basename(shortcut_action)}."
            else:
                # Treat as a redirected text command
                query = shortcut_action
                q = query.lower().strip()

        # 2. Check Plugin System command hooks
        plugin_response = self.plugins.execute_plugin_command(query)
        if plugin_response:
            return plugin_response

        # 3. System Automation Commands (Volume, Brightness, Power)
        if "volume" in q:
            match = re.search(r'\d+', q)
            if match:
                val = int(match.group())
                self.system.set_volume(val)
                return f"System volume adjusted to {val} percent."
            elif "mute" in q:
                self.system.set_volume(0)
                return "System audio muted."
            elif "up" in q:
                curr = self.system.get_volume()
                self.system.set_volume(curr + 15)
                return "Increasing system volume."
            elif "down" in q:
                curr = self.system.get_volume()
                self.system.set_volume(max(0, curr - 15))
                return "Decreasing system volume."
                
        elif "brightness" in q:
            match = re.search(r'\d+', q)
            if match:
                val = int(match.group())
                self.system.set_brightness(val)
                return f"Display brightness set to {val} percent."
            elif "up" in q:
                curr = self.system.get_brightness()
                self.system.set_brightness(curr + 15)
                return "Increasing display brightness."
            elif "down" in q:
                curr = self.system.get_brightness()
                self.system.set_brightness(max(0, curr - 15))
                return "Decreasing display brightness."

        elif "lock screen" in q or "lock pc" in q or "lock computer" in q:
            self.system.lock_screen()
            return "Locking system workstation, Sir."
            
        elif "sleep computer" in q or "sleep mode" in q:
            self.system.sleep_pc()
            return "Entering system sleep state."

        elif "shutdown" in q:
            self.system.shutdown()
            return "Initiating full shutdown sequence. Goodbye, Sir."
            
        elif "restart" in q:
            self.system.restart()
            return "Rebooting mainframe systems. Restarting PC."

        # 4. App Launch / Close Commands
        elif q.startswith("open "):
            app_to_open = q.replace("open ", "").strip()
            # Special web checks
            if "google" in app_to_open and "search" not in app_to_open:
                self.apps.open_website("google.com")
                return "Opening Google in browser."
            elif "youtube" in app_to_open and "search" not in app_to_open:
                self.apps.open_website("youtube.com")
                return "Opening YouTube."
            elif app_to_open.startswith("www.") or app_to_open.endswith((".com", ".net", ".org", ".in")):
                self.apps.open_website(app_to_open)
                return f"Opening web portal {app_to_open}."
            else:
                success = self.apps.open_app(app_to_open)
                if success:
                    return f"Launching application: {app_to_open}."
                return f"I was unable to locate or open the application: {app_to_open}."

        elif q.startswith("close "):
            app_to_close = q.replace("close ", "").strip()
            success = self.apps.close_app(app_to_close)
            if success:
                return f"Terminating process: {app_to_close}."
            return f"Process '{app_to_close}' could not be terminated."

        # 5. Web Search queries
        elif "google search" in q or "search google for" in q:
            query_term = q.replace("google search", "").replace("search google for", "").strip()
            self.apps.search_google(query_term)
            return f"Searching Google index for: '{query_term}'."
            
        elif "youtube search" in q or "search youtube for" in q:
            query_term = q.replace("youtube search", "").replace("search youtube for", "").strip()
            self.apps.search_youtube(query_term)
            return f"Searching YouTube channels for: '{query_term}'."

        # 6. Screen Intelligence & Screenshots
        elif "screenshot" in q or "screen cap" in q:
            path = self.screen_intel.capture_screen()
            if "explain" in q or "analyze" in q or "what is on my screen" in q:
                # Vision analysis requested
                analysis = self.screen_intel.analyze_screen_with_gpt(path)
                return analysis
            return f"Screenshot successfully saved to: {os.path.basename(path)}."

        # 7. Personality profile selection
        elif "set persona" in q or "change mode" in q:
            for mode in ["default", "stark", "scientific", "military"]:
                if mode in q:
                    self.ai.set_persona(mode)
                    return f"Personality matrices updated. Jarvis X is now running in {mode.upper()} mode, Sir."

        # 8. Mission Checklist Commands
        elif "create mission" in q:
            m_name = query.replace("create mission", "", 1).replace("Create Mission", "", 1).strip()
            if m_name:
                return self.missions.create_mission(m_name)
            return "Please provide a valid mission name. Example: 'Create mission Jarvis X'"
            
        elif "add task" in q:
            # Format: 'add task [task details] to mission [mission name]'
            match = re.search(r'add task (.+?) to mission (.+)', query, re.IGNORECASE)
            if match:
                task_desc = match.group(1).strip()
                m_name = match.group(2).strip()
                return self.missions.add_mission_task(m_name, task_desc)
            return "Please use the format: 'Add task [details] to mission [name]'"
            
        elif "complete task" in q:
            match = re.search(r'\d+', q)
            if match:
                t_id = int(match.group())
                return self.missions.complete_mission_task(t_id)
            return "Please specify the task ID number. Example: 'Complete task 4'"
            
        elif "mission report" in q:
            m_name = query.replace("mission report", "", 1).replace("Mission Report", "", 1).strip()
            if m_name:
                return self.missions.get_mission_report(m_name)
            return "Please specify the mission name. Example: 'Mission report Jarvis X'"

        # 9. Emergency Panic Trigger
        elif "emergency" in q or "panic trigger" in q:
            # Send emergency emails
            success = self.email.send_emergency_alert(self.emergency_contacts, "JARVIS X Desktop Emergency Mode Activated")
            if success:
                return "EMERGENCY PROTOCOLS INITIATED. Alert notifications dispatched to trusted contact contacts."
            return "Emergency protocol failed. Please configure SMTP email credentials in environment variables."

        # 10. Memory Vault Commands
        elif "save password" in q or "save secret" in q:
            # Format: 'save password [title] value [secret]'
            match = re.search(r'save (?:password|secret) (.+?) value (.+)', query, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                secret = match.group(2).strip()
                enc_secret = self.vault.encrypt(secret)
                success = self.db.save_vault_item(title, enc_secret, category='password')
                if success:
                    return f"Secret payload '{title}' has been successfully encrypted and committed to the database vault."
            return "Secret could not be stored. Format: 'Save password [title] value [secret]'"

        elif "retrieve password" in q or "retrieve secret" in q:
            title = query.replace("retrieve password", "", 1).replace("retrieve secret", "", 1).replace("Retrieve Password", "", 1).replace("Retrieve Secret", "", 1).strip()
            items = self.db.get_vault_items(category='password')
            for item in items:
                if item["title"].lower() == title.lower():
                    dec_val = self.vault.decrypt(item["encrypted_payload"])
                    return f"Decrypted Secret for '{title}': '{dec_val}'"
            return f"No credential found matching name '{title}'."

        # 11. Code execution sandbox demo (safe Python evaluation)
        elif "execute python" in q or "run code" in q:
            code = query.replace("execute python", "", 1).replace("run code", "", 1).strip()
            return self._execute_safe_code(code)

        # 12. Default to GPT-powered conversational agent
        else:
            return self.ai.chat(query)

    def _execute_safe_code(self, code_str: str) -> str:
        """Executes a single line or short block of Python code inside a restricted context."""
        print(f"[Orchestrator] Safely executing python code: {code_str}")
        
        # Clean markdown code block wraps if present
        code = code_str.replace("```python", "").replace("```", "").strip()
        
        # Build restricted environment
        safe_globals = {
            "__builtins__": {
                "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
                "chr": chr, "dict": dict, "dir": dir, "divmod": divmod, "enumerate": enumerate,
                "filter": filter, "float": float, "format": format, "hash": hash, "hex": hex,
                "id": id, "int": int, "isinstance": isinstance, "issubclass": issubclass,
                "len": len, "list": list, "map": map, "max": max, "min": min, "next": next,
                "oct": oct, "ord": ord, "pow": pow, "range": range, "repr": repr, "reversed": reversed,
                "round": round, "set": set, "slice": slice, "sorted": sorted, "str": str, "sum": sum,
                "tuple": tuple, "zip": zip, "print": print
            },
            "math": __import__("math"),
            "datetime": __import__("datetime")
        }
        
        # Redirect stdout to capture prints
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        try:
            # We use exec. To return a result, if it's an expression we eval it,
            # otherwise we execute it.
            # Try to compile as eval first:
            try:
                code_compiled = compile(code, "<string>", "eval")
                res = eval(code_compiled, safe_globals, {})
                sys.stdout = old_stdout
                output = redirected_output.getvalue().strip()
                if output:
                    return f"[Stdout Output]:\n{output}\n[Result]: {res}"
                return f"[Result]: {res}"
            except SyntaxError:
                # Run as multi-line exec block
                code_compiled = compile(code, "<string>", "exec")
                exec(code_compiled, safe_globals, {})
                sys.stdout = old_stdout
                output = redirected_output.getvalue().strip()
                if output:
                    return f"[Stdout Output]:\n{output}"
                return "Execution complete (No output yielded)."
        except Exception as e:
            sys.stdout = old_stdout
            return f"Execution error in sandbox: {e}"
