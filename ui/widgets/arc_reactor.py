import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush

class ArcReactorWidget(QWidget):
    """Futuristic animated Iron Man Arc Reactor core representing JARVIS status."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"  # 'idle', 'listening', 'processing', 'speaking'
        self.angle_outer = 0.0
        self.angle_inner = 0.0
        self.pulse_val = 1.0
        self.pulse_dir = 1
        self.speak_amplitude = 0.0
        
        # Core color palette
        self.color_neon = QColor(0, 210, 211)      # Cyan glow
        self.color_accent = QColor(233, 69, 96)    # Red highlights
        
        # Set up animation timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 FPS

    def set_state(self, state: str):
        """Update voice state and alter reactor behavior parameters."""
        self.state = state.lower().strip()
        self.update()

    def update_animation(self):
        """Calculates speeds, angles, and pulse properties for each frame."""
        # 1. Update rotation angles based on state
        if self.state == "listening":
            self.angle_outer -= 4.0   # Fast spin CCW
            self.angle_inner += 6.0   # Fast spin CW
        elif self.state == "processing":
            self.angle_outer += 8.0   # Erratic fast spin
            self.angle_inner -= 10.0
        elif self.state == "speaking":
            self.angle_outer -= 1.5
            self.angle_inner += 2.0
        else: # 'idle'
            self.angle_outer -= 0.5   # Slow, calm spin
            self.angle_inner += 0.8
            
        # 2. Update center glow pulsing values
        if self.state == "listening":
            pulse_speed = 0.06
        elif self.state == "processing":
            pulse_speed = 0.12
        else: # 'idle' or 'speaking'
            pulse_speed = 0.02
            
        self.pulse_val += self.pulse_dir * pulse_speed
        if self.pulse_val >= 1.3:
            self.pulse_dir = -1
        elif self.pulse_val <= 0.7:
            self.pulse_dir = 1
            
        # 3. If speaking, generate dynamic audio amplitude spikes
        if self.state == "speaking":
            self.speak_amplitude = random.uniform(0.3, 1.2)
        else:
            self.speak_amplitude = 0.0
            
        self.update()  # Request repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        side = min(width, height)
        
        # Center coordinates
        cx = width / 2.0
        cy = height / 2.0
        
        # Outer bounds
        painter.translate(cx, cy)
        
        # Draw background ring glow
        radial_grad = QRadialGradient(0, 0, side / 2.0)
        glow_color = QColor(self.color_neon)
        if self.state == "listening":
            glow_color = QColor(0, 210, 211, 40)
        elif self.state == "processing":
            glow_color = QColor(self.color_accent.red(), self.color_accent.green(), self.color_accent.blue(), 50)
        else:
            glow_color = QColor(0, 210, 211, 20)
            
        radial_grad.setColorAt(0.0, glow_color)
        radial_grad.setColorAt(0.8, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(radial_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(-side/2.0, -side/2.0, side, side))
        
        # --- DRAW LAYER 1: OUTER SEGMENTED RING ---
        painter.save()
        painter.rotate(self.angle_outer)
        pen_outer = QPen(self.color_neon, 2)
        pen_outer.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen_outer)
        r_outer = side * 0.40
        painter.drawEllipse(QRectF(-r_outer, -r_outer, r_outer*2, r_outer*2))
        painter.restore()
        
        # --- DRAW LAYER 2: INTERMEDIATE REVOLVING SHARDS ---
        painter.save()
        painter.rotate(self.angle_inner)
        pen_mid = QPen(self.color_neon, 3)
        painter.setPen(pen_mid)
        r_mid = side * 0.30
        
        # Draw 8 segmented mechanical shards
        for i in range(8):
            painter.rotate(45)
            # Draw arc segments
            painter.drawArc(QRectF(-r_mid, -r_mid, r_mid*2, r_mid*2), 0 * 16, 25 * 16)
        painter.restore()
        
        # --- DRAW LAYER 3: INNER ACTIVE RING ---
        # Speaking mode expands/contracts this ring dynamically
        r_inner = side * 0.20
        if self.state == "speaking":
            r_inner += (self.speak_amplitude * 15.0)
        elif self.state == "listening":
            r_inner *= self.pulse_val
            
        pen_inner = QPen(self.color_neon, 1)
        if self.state == "processing":
            pen_inner.setColor(self.color_accent)
        painter.setPen(pen_inner)
        painter.drawEllipse(QRectF(-r_inner, -r_inner, r_inner*2, r_inner*2))
        
        # --- DRAW LAYER 4: REACTOR CORE GLOW (CENTER SYMBOL) ---
        r_core = side * 0.10 * self.pulse_val
        if self.state == "speaking":
            r_core += (self.speak_amplitude * 8.0)
            
        core_grad = QRadialGradient(0, 0, r_core)
        if self.state == "processing":
            core_grad.setColorAt(0.0, QColor(255, 255, 255))
            core_grad.setColorAt(0.4, self.color_accent)
            core_grad.setColorAt(1.0, QColor(233, 69, 96, 0))
        else:
            core_grad.setColorAt(0.0, QColor(255, 255, 255))
            core_grad.setColorAt(0.3, self.color_neon)
            core_grad.setColorAt(1.0, QColor(0, 210, 211, 0))
            
        painter.setBrush(QBrush(core_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QRectF(-r_core, -r_core, r_core*2, r_core*2))
        
        # Draw micro crosshairs overlay
        pen_cross = QPen(QColor(255, 255, 255, 100), 1)
        painter.setPen(pen_cross)
        line_len = int(side * 0.05)
        painter.drawLine(0, -line_len, 0, line_len)
        painter.drawLine(-line_len, 0, line_len, 0)
