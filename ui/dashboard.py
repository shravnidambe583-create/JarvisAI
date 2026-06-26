import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QGridLayout, QHBoxLayout, 
                             QVBoxLayout, QFrame, QLabel, QLineEdit, QPushButton, 
                             QListWidget, QStackedLayout, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSlot

# Custom visual widgets
from ui.widgets.particle_bg import ParticleBackground
from ui.widgets.arc_reactor import ArcReactorWidget
from ui.widgets.waveform import WaveformWidget
from ui.widgets.typewriter import TypewriterLabel
from ui.widgets.stats_panel import SystemStatsPanel
from ui.style import QSS_STYLESHEET

class JarvisDashboard(QMainWindow):
    """The main glassmorphic holographic dashboard UI for JARVIS X."""
    
    def __init__(self, orchestrator=None):
        super().__init__()
        # Use provided orchestrator or alert if missing
        self.orchestrator = orchestrator
        
        # Configure window settings
        self.setWindowTitle("JARVIS X - Mainframe Interface")
        self.resize(1200, 780)
        self.setMinimumSize(1000, 680)
        
        # Apply custom styling (QSS)
        self.setStyleSheet(QSS_STYLESHEET)
        
        self.init_ui()
        self.connect_orchestrator()

    def init_ui(self):
        """Assembles layout widgets on top of the particle background."""
        # 1. Base Layer Stacked Layout (Background + Foreground)
        self.base_widget = QWidget()
        self.setCentralWidget(self.base_widget)
        self.stacked_layout = QStackedLayout(self.base_widget)
        self.stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
        # Layer 1: Animated Particle Starfield
        self.bg_particles = ParticleBackground()
        self.stacked_layout.addWidget(self.bg_particles)
        
        # Layer 2: Main HUD Panel
        self.hud_foreground = QWidget()
        self.hud_foreground.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.stacked_layout.addWidget(self.hud_foreground)
        
        # Foreground Grid Layout
        main_layout = QGridLayout(self.hud_foreground)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # --- LEFT PANEL: UTILITIES ---
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout, 0, 0, 1, 1)
        main_layout.setColumnStretch(0, 1) # Column widths
        
        # Weather Panel
        self.weather_frame = QFrame()
        self.weather_frame.setObjectName("HoloPanel")
        weather_layout = QVBoxLayout(self.weather_frame)
        lbl_w_title = QLabel("ENVIRONMENT DIAGNOSTICS")
        lbl_w_title.setObjectName("HoloTitle")
        self.lbl_weather_details = QLabel("Location: New Delhi, India\nWeather: Clear Skies, 32°C\nHumidity: 45%\nStatus: Satellite Connected")
        self.lbl_weather_details.setStyleSheet("color: #a0a0b0; font-size: 11px;")
        weather_layout.addWidget(lbl_w_title)
        weather_layout.addWidget(self.lbl_weather_details)
        left_layout.addWidget(self.weather_frame)
        
        # Active Goals / Tasks Panel
        self.task_frame = QFrame()
        self.task_frame.setObjectName("HoloPanel")
        task_layout = QVBoxLayout(self.task_frame)
        lbl_t_title = QLabel("MISSION CHECKLIST")
        lbl_t_title.setObjectName("HoloTitle")
        self.task_list = QListWidget()
        task_layout.addWidget(lbl_t_title)
        task_layout.addWidget(self.task_list)
        
        # Task actions
        task_btns = QHBoxLayout()
        btn_add_t = QPushButton("ADD TASK")
        btn_complete_t = QPushButton("COMPLETE TASK")
        task_btns.addWidget(btn_add_t)
        task_btns.addWidget(btn_complete_t)
        task_layout.addLayout(task_btns)
        left_layout.addWidget(self.task_frame, stretch=2)
        
        btn_add_t.clicked.connect(self.add_task_dialog)
        btn_complete_t.clicked.connect(self.complete_task_dialog)
        
        # --- CENTER PANEL: JARVIS CORE INTERFACE ---
        center_layout = QVBoxLayout()
        main_layout.addLayout(center_layout, 0, 1, 1, 1)
        main_layout.setColumnStretch(1, 2) # Center gets double width
        
        # Reactor core frame
        self.core_frame = QFrame()
        self.core_frame.setObjectName("HoloPanel")
        core_box = QVBoxLayout(self.core_frame)
        
        # Holographic circular AI core
        self.arc_reactor = ArcReactorWidget()
        self.arc_reactor.setMinimumSize(220, 220)
        core_box.addWidget(self.arc_reactor, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Waveform voice visualizer
        self.waveform = WaveformWidget()
        self.waveform.setFixedHeight(65)
        core_box.addWidget(self.waveform)
        
        center_layout.addWidget(self.core_frame, stretch=1)
        
        # Dialogue typewriter console
        self.console_frame = QFrame()
        self.console_frame.setObjectName("HoloPanel")
        console_box = QVBoxLayout(self.console_frame)
        
        lbl_c_title = QLabel("JARVIS OUTPUT CONSOLE")
        lbl_c_title.setObjectName("HoloTitle")
        self.typewriter_lbl = TypewriterLabel()
        self.typewriter_lbl.start_typing("System initialized. JARVIS X stands ready. Awaiting instructions...")
        
        console_box.addWidget(lbl_c_title)
        console_box.addWidget(self.typewriter_lbl)
        center_layout.addWidget(self.console_frame, stretch=1)
        
        # --- RIGHT PANEL: DIAGNOSTICS & MEMORY ---
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout, 0, 2, 1, 1)
        main_layout.setColumnStretch(2, 1)
        
        # System Hardware Stats Widget
        self.stats_frame = QFrame()
        self.stats_frame.setObjectName("HoloPanel")
        stats_layout = QVBoxLayout(self.stats_frame)
        lbl_s_title = QLabel("MAINFRAME STATUS")
        lbl_s_title.setObjectName("HoloTitle")
        self.stats_panel = SystemStatsPanel()
        self.stats_panel.setMinimumSize(180, 180)
        stats_layout.addWidget(lbl_s_title)
        stats_layout.addWidget(self.stats_panel)
        right_layout.addWidget(self.stats_frame)
        
        # Memory Vault Panel
        self.vault_frame = QFrame()
        self.vault_frame.setObjectName("VaultPanel")
        vault_layout = QVBoxLayout(self.vault_frame)
        lbl_v_title = QLabel("SECURE CRYPTO VAULT")
        lbl_v_title.setObjectName("HoloTitle")
        lbl_v_title.setStyleSheet("color: #e94560;")
        
        self.vault_keys_list = QListWidget()
        self.vault_keys_list.setStyleSheet("QListWidget { color: #ff6b81; }")
        
        vault_layout.addWidget(lbl_v_title)
        vault_layout.addWidget(self.vault_keys_list)
        
        vault_btns = QHBoxLayout()
        btn_save_pw = QPushButton("LOCK SECRET")
        btn_save_pw.setObjectName("WarningButton")
        btn_view_pw = QPushButton("UNLOCK")
        vault_btns.addWidget(btn_save_pw)
        vault_btns.addWidget(btn_view_pw)
        vault_layout.addLayout(vault_btns)
        
        btn_save_pw.clicked.connect(self.save_vault_dialog)
        btn_view_pw.clicked.connect(self.view_vault_dialog)
        
        right_layout.addWidget(self.vault_frame, stretch=1)
        
        # --- BOTTOM PANEL: INPUT / COMMAND BAR ---
        self.input_frame = QFrame()
        self.input_frame.setObjectName("HoloPanel")
        input_layout = QHBoxLayout(self.input_frame)
        
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Transmit command string or type dialogue...")
        btn_transmit = QPushButton("TRANSMIT")
        
        # Control Buttons
        self.btn_listen = QPushButton("LISTEN")
        self.btn_login = QPushButton("SECURITY SYNC")
        self.btn_emergency = QPushButton("EMERGENCY")
        self.btn_emergency.setObjectName("WarningButton")
        
        input_layout.addWidget(self.cmd_input, stretch=3)
        input_layout.addWidget(btn_transmit)
        input_layout.addWidget(self.btn_listen)
        input_layout.addWidget(self.btn_login)
        input_layout.addWidget(self.btn_emergency)
        
        main_layout.addWidget(self.input_frame, 1, 0, 1, 3)
        
        # Connect Actions
        self.cmd_input.returnPressed.connect(self.transmit_command)
        btn_transmit.clicked.connect(self.transmit_command)
        self.btn_listen.clicked.connect(self.trigger_listen)
        self.btn_login.clicked.connect(self.trigger_face_sync)
        self.btn_emergency.clicked.connect(self.trigger_emergency)
        
        self.update_task_display()
        self.update_vault_display()

    def connect_orchestrator(self):
        """Bind UI slots to orchestrator signals."""
        if not self.orchestrator:
            return
            
        # Connect logs
        self.orchestrator.ui_log.connect(self.receive_log)
        # Connect voice state changes
        self.orchestrator.voice_state_changed.connect(self.receive_voice_state)

    @pyqtSlot(str, str)
    def receive_log(self, text: str, category: str):
        """Append log events to the console display with styling."""
        if category == "user":
            formatted = f"<font color='#ffffff'>👤 YOU:</font> {text}"
        elif category == "jarvis":
            formatted = f"<font color='#00d2d3'>🤖 JARVIS X:</font> {text}"
            self.typewriter_lbl.start_typing(text)
            self.update_task_display()
            self.update_vault_display()
            return
        elif category == "error":
            formatted = f"<font color='#e94560'>🚨 ALARM:</font> {text}"
        elif category == "warning":
            formatted = f"<font color='#feca57'>⚠️ WARNING:</font> {text}"
        else:
            formatted = f"<font color='#a0a0b0'>⚙️ SYSTEM:</font> {text}"
            
        self.typewriter_lbl.setHtml(formatted)

    @pyqtSlot(str)
    def receive_voice_state(self, state: str):
        """Route state variables to core reactor and waveform widgets."""
        self.arc_reactor.set_state(state)
        self.waveform.set_state(state)
        
        if state == "listening":
            self.btn_listen.setText("LISTENING")
            self.btn_listen.setStyleSheet("background-color: rgba(0, 210, 211, 0.4);")
        else:
            self.btn_listen.setText("LISTEN")
            self.btn_listen.setStyleSheet("")

    def transmit_command(self):
        """Extracts text inputs and submits them to the orchestrator command parser."""
        text = self.cmd_input.text().strip()
        if not text:
            return
            
        self.cmd_input.clear()
        
        if self.orchestrator:
            self.orchestrator.process_command(text)
        else:
            self.receive_log(text, "user")
            self.receive_log("Main orchestration server is offline.", "error")

    def trigger_listen(self):
        """Force triggers audio microphone capture loop."""
        if self.orchestrator:
            self.orchestrator.activate_listening()

    def trigger_face_sync(self):
        """Launches camera authentication verification face scan."""
        if self.orchestrator:
            self.typewriter_lbl.setHtml("System: Scanning camera feed for verified locks...")
            # Run in separate thread to prevent freezing
            import threading
            threading.Thread(target=self._run_face_auth_flow, daemon=True).start()

    def _run_face_auth_flow(self):
        success = self.orchestrator.face_auth.authenticate()
        if success:
            self.orchestrator.ui_log.emit("Security cleared. Interface unlocked, Sir.", "jarvis")
        else:
            self.orchestrator.ui_log.emit("Lock match failed. Camera captured security snapshots.", "error")

    def trigger_emergency(self):
        """Instantly invokes system critical emergency notification protocols."""
        if self.orchestrator:
            self.orchestrator.process_command("emergency")

    # --- DB Visual Updates ---
    def update_task_display(self):
        """Re-reads task checklist from SQLite database."""
        if not self.orchestrator:
            return
        self.task_list.clear()
        try:
            tasks = self.orchestrator.db.get_tasks()
            for t in tasks:
                status = "✅" if t["status"] == "completed" else "⬜"
                prefix = f"[{t['mission_name']}] " if t['mission_name'] else ""
                self.task_list.addItem(f"{status} [ID: {t['id']}] {prefix}{t['task_desc']}")
        except Exception:
            pass

    def update_vault_display(self):
        """Re-reads password vault directories from SQLite database."""
        if not self.orchestrator:
            return
        self.vault_keys_list.clear()
        try:
            items = self.orchestrator.db.get_vault_items()
            for item in items:
                self.vault_keys_list.addItem(f"🔒 {item['title']} ({item['category']})")
        except Exception:
            pass

    # --- Interactive Dialogs ---
    def add_task_dialog(self):
        """Popup dialog to add a task from UI."""
        text, ok = QInputDialog.getText(self, "Add Task", "Enter task description:")
        if ok and text.strip():
            mission, ok_m = QInputDialog.getText(self, "Mission Assignment", "Enter mission name (optional):")
            m_name = mission.strip() if ok_m and mission.strip() else None
            self.orchestrator.db.add_task(text, mission_name=m_name)
            self.update_task_display()

    def complete_task_dialog(self):
        """Popup dialog to complete a task from UI."""
        text, ok = QInputDialog.getText(self, "Complete Task", "Enter Task ID number:")
        if ok and text.strip():
            try:
                t_id = int(text.strip())
                self.orchestrator.missions.complete_mission_task(t_id)
                self.update_task_display()
            except ValueError:
                pass

    def save_vault_dialog(self):
        """Popup dialog to lock a secret into the Memory Vault."""
        title, ok_t = QInputDialog.getText(self, "Secure Secret", "Enter title/label:")
        if ok_t and title.strip():
            secret, ok_s = QInputDialog.getText(self, "Secure Secret", "Enter secret payload (password/note):")
            if ok_s and secret.strip():
                enc_secret = self.orchestrator.vault.encrypt(secret)
                self.orchestrator.db.save_vault_item(title, enc_secret, category='password')
                self.update_vault_display()

    def view_vault_dialog(self):
        """Popup dialog to decrypt and show a secret from the Vault."""
        title, ok = QInputDialog.getText(self, "Unlock Secret", "Enter label/title to unlock:")
        if ok and title.strip():
            items = self.orchestrator.db.get_vault_items()
            for item in items:
                if item["title"].lower() == title.lower().strip():
                    dec_val = self.orchestrator.vault.decrypt(item["encrypted_payload"])
                    # Show decrypted secret in console
                    self.receive_log(f"Decrypted payload for '{item['title']}': '{dec_val}'", "warning")
                    return
            self.receive_log(f"Label '{title}' not found in vault indexes.", "error")
