import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath

class WaveformWidget(QWidget):
    """Futuristic multi-phase voice wave visualizer responding to JARVIS voice states."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"
        self.phase = 0.0
        self.max_amplitude = 15.0
        self.target_amplitude = 15.0
        self.current_amplitude = 15.0
        self.frequency = 0.05
        
        # Color palettes
        self.colors = [
            QColor(0, 210, 211, 150),  # Bright Cyan
            QColor(84, 160, 255, 100),  # Soft Blue
            QColor(0, 210, 211, 50)     # Faded Cyan background
        ]
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(20)  # ~50 FPS

    def set_state(self, state: str):
        self.state = state.lower().strip()
        
        # Configure target sizes based on voice states
        if self.state == "listening":
            self.target_amplitude = 40.0
            self.frequency = 0.12
        elif self.state == "speaking":
            self.target_amplitude = 35.0
            self.frequency = 0.08
        elif self.state == "processing":
            self.target_amplitude = 25.0
            self.frequency = 0.20
        else: # 'idle'
            self.target_amplitude = 10.0
            self.frequency = 0.04

    def update_wave(self):
        # Shift phase angle
        if self.state == "processing":
            self.phase += 0.35  # Fast jitter
        elif self.state == "listening":
            self.phase += 0.25
        else:
            self.phase += 0.12  # Steady smooth shift
            
        # Smoothly interpolate amplitude transitions
        diff = self.target_amplitude - self.current_amplitude
        self.current_amplitude += diff * 0.15
        
        # If speaking, inject audio fluctuation noise
        if self.state == "speaking":
            self.current_amplitude = self.target_amplitude * random.uniform(0.4, 1.2)
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        cy = height / 2.0
        
        # Draw base zero-axis reference line
        pen_ref = QPen(QColor(0, 210, 211, 30), 1)
        painter.setPen(pen_ref)
        painter.drawLine(0, int(cy), width, int(cy))
        
        # Draw 3 overlay waves
        for wave_idx in range(3):
            path = QPainterPath()
            path.moveTo(0, cy)
            
            # Select settings for this wave instance
            amplitude = self.current_amplitude * (1.0 - wave_idx * 0.3)
            phase_offset = self.phase + (wave_idx * math.pi / 3.0)
            
            # If listening, add extra high frequency noise jitters
            noise_scale = 8.0 if self.state == "listening" else 0.0
            
            for x in range(0, width, 4):
                # Calculate sine wave position
                # Normalized coordinate (0 to 1) for shaping envelope
                norm_x = x / float(width)
                
                # Apply envelope so the wave pinches to zero at the left/right boundaries
                envelope = math.sin(norm_x * math.pi)
                
                angle = (x * self.frequency) + phase_offset
                y = cy + (amplitude * math.sin(angle) * envelope)
                
                # Add random noise spikes if user is speaking/mic active
                if noise_scale > 0:
                    y += random.uniform(-noise_scale, noise_scale) * envelope
                    
                path.lineTo(float(x), float(y))
                
            path.lineTo(float(width), float(cy))
            
            pen_wave = QPen(self.colors[wave_idx], 2 if wave_idx == 0 else 1)
            painter.setPen(pen_wave)
            painter.drawPath(path)
