import random
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen

class ParticleBackground(QWidget):
    """Futuristic floating particles connected by thin lines, overlaid with a grid."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.num_particles = 45
        self.max_distance = 90.0  # Max distance to draw lines between nodes
        self.grid_size = 60
        
        # Color definitions
        self.color_particle = QColor(0, 210, 211, 80)
        self.color_line = QColor(0, 210, 211, 40)
        self.color_grid = QColor(0, 210, 211, 10)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(33)  # ~30 FPS

    def init_particles(self):
        """Pre-populate particles list with positions based on current widget sizes."""
        self.particles = []
        w = self.width()
        h = self.height()
        
        if w < 50 or h < 50:
            return
            
        for _ in range(self.num_particles):
            self.particles.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "dx": random.uniform(-0.4, 0.4),
                "dy": random.uniform(-0.4, 0.4),
                "size": random.uniform(1.5, 3.5),
                "alpha": random.randint(50, 150)
            })

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.init_particles()

    def update_particles(self):
        w = self.width()
        h = self.height()
        
        if not self.particles:
            self.init_particles()
            return
            
        for p in self.particles:
            # Move particle
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            
            # Wrap around boundaries
            if p["x"] < 0:
                p["x"] = w
            elif p["x"] > w:
                p["x"] = 0
                
            if p["y"] < 0:
                p["y"] = h
            elif p["y"] > h:
                p["y"] = 0
                
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # 1. Fill deep space background
        painter.fillRect(0, 0, w, h, QColor(10, 10, 25))
        
        # 2. Draw subtle grid grid lines
        pen_grid = QPen(self.color_grid, 1)
        painter.setPen(pen_grid)
        
        for x in range(0, w, self.grid_size):
            painter.drawLine(x, 0, x, h)
        for y in range(0, h, self.grid_size):
            painter.drawLine(0, y, w, y)
            
        # 3. Draw connecting lines between close particles
        pen_line = QPen()
        pen_line.setWidthF(0.8)
        
        num_p = len(self.particles)
        for i in range(num_p):
            p1 = self.particles[i]
            for j in range(i + 1, num_p):
                p2 = self.particles[j]
                
                # Euclidean distance
                dist = math.hypot(p1["x"] - p2["x"], p1["y"] - p2["y"])
                if dist < self.max_distance:
                    # Calculate fading alpha based on distance
                    alpha_factor = 1.0 - (dist / self.max_distance)
                    line_alpha = int(p1["alpha"] * 0.25 * alpha_factor)
                    
                    self.color_line.setAlpha(line_alpha)
                    pen_line.setColor(self.color_line)
                    painter.setPen(pen_line)
                    painter.drawLine(QPointF(p1["x"], p1["y"]), QPointF(p2["x"], p2["y"]))
                    
        # 4. Draw individual particle nodes
        for p in self.particles:
            c = QColor(self.color_particle)
            c.setAlpha(p["alpha"])
            painter.setBrush(c)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(p["x"], p["y"]), p["size"], p["size"])
