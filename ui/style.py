# Glassmorphism QSS styling for JARVIS X
# Provides glowing borders, transparency, and dark-futuristic colors

QSS_STYLESHEET = """
QMainWindow {
    background-color: #0d0d1a;
}

/* Glassmorphic Holo Panel styling */
QFrame#HoloPanel {
    background-color: rgba(16, 21, 38, 0.65);
    border: 1px solid rgba(0, 210, 211, 0.25);
    border-radius: 8px;
}

QFrame#HoloPanel:hover {
    border: 1px solid rgba(0, 210, 211, 0.50);
}

/* Glassmorphic Vault/Security Panel */
QFrame#VaultPanel {
    background-color: rgba(26, 26, 46, 0.85);
    border: 1px solid rgba(233, 69, 96, 0.35);
    border-radius: 8px;
}

/* Standard scrollbars with neon styling */
QScrollBar:vertical {
    border: none;
    background: rgba(16, 21, 38, 0.5);
    width: 6px;
    margin: 0px 0 0px 0;
}
QScrollBar::handle:vertical {
    background: rgba(0, 210, 211, 0.4);
    min-height: 20px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(0, 210, 211, 0.8);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Buttons styling with neon blue hover glow */
QPushButton {
    background-color: rgba(10, 30, 60, 0.4);
    color: #ffffff;
    border: 1px solid #00d2d3;
    border-radius: 4px;
    padding: 6px 12px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1px;
}

QPushButton:hover {
    background-color: rgba(0, 210, 211, 0.2);
    border: 1px solid #00d2d3;
    box-shadow: 0 0 10px #00d2d3;
}

QPushButton:pressed {
    background-color: rgba(0, 210, 211, 0.4);
}

/* Warning buttons (Red/Emergency) */
QPushButton#WarningButton {
    border: 1px solid #e94560;
    color: #e94560;
    background-color: rgba(233, 69, 96, 0.1);
}

QPushButton#WarningButton:hover {
    background-color: rgba(233, 69, 96, 0.3);
    border: 1px solid #ff6b81;
}

/* Text Inputs / LineEdits styling */
QLineEdit {
    background-color: rgba(10, 10, 20, 0.8);
    border: 1px solid rgba(0, 210, 211, 0.3);
    border-radius: 4px;
    padding: 6px;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QLineEdit:focus {
    border: 1px solid #00d2d3;
}

/* Labels styling */
QLabel {
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QLabel#HoloTitle {
    color: #00d2d3;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
    border-bottom: 1px solid rgba(0, 210, 211, 0.15);
    padding-bottom: 4px;
}

/* Table views / lists */
QListWidget {
    background-color: transparent;
    border: none;
    color: #a0a0b0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QListWidget::item {
    padding: 5px;
    border-bottom: 1px solid rgba(0, 210, 211, 0.05);
}

QListWidget::item:hover {
    background-color: rgba(0, 210, 211, 0.1);
    color: #ffffff;
}
"""
