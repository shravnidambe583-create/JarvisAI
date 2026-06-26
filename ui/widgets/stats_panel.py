import psutil
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

class SystemStatsPanel(QWidget):
    """Draws sleek circular progress meters for CPU, RAM, Disk, and Battery diagnostics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu = 0.0
        self.ram = 0.0
        self.disk = 0.0
        self.battery = 100
        self.has_battery = False
        
        # Color schemes
        self.color_neon = QColor(0, 210, 211)   # Cyan
        self.color_accent = QColor(233, 69, 96) # Red
        self.color_dim = QColor(0, 210, 211, 40)
        
        # Diagnostics update timer (every 2 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_diagnostics)
        self.timer.start(2000)
        
        self.read_diagnostics()

    def read_diagnostics(self):
        """Queries hardware status using psutil library."""
        try:
            self.cpu = psutil.cpu_percent()
            self.ram = psutil.virtual_memory().percent
            self.disk = psutil.disk_usage('/').percent
            
            bat = psutil.sensors_battery()
            if bat:
                self.battery = bat.percent
                self.has_battery = True
            else:
                self.has_battery = False
        except Exception as e:
            print(f"[Stats] Error reading diagnostics: {e}")
            
        self.update()  # Request repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Divide space into 4 squares (2x2 grid) for meters
        box_w = w / 2.0
        box_h = h / 2.0
        
        # Coordinates of centers
        centers = [
            (box_w / 2.0, box_h / 2.0, "CPU", self.cpu),
            (box_w + box_w / 2.0, box_h / 2.0, "RAM", self.ram),
            (box_w / 2.0, box_h + box_h / 2.0, "DISK", self.disk),
            (box_w + box_w / 2.0, box_h + box_h / 2.0, "BAT", self.battery if self.has_battery else 100.0)
        ]
        
        # Radius of circles
        r = min(box_w, box_h) * 0.35
        
        for cx, cy, label, val in centers:
            # Skip battery draw if system has no battery sensor, drawing mock uptime instead
            if label == "BAT" and not self.has_battery:
                # Mock uptime or static
                val = 100.0
                display_label = "PWR"
                display_text = "AC"
            else:
                display_label = label
                display_text = f"{int(val)}%"
                
            # 1. Draw background dim circle
            pen_bg = QPen(self.color_dim, 4)
            painter.setPen(pen_bg)
            painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
            
            # 2. Draw active arc representing the stat
            # Determine color based on stat load
            if val > 85.0:
                pen_color = self.color_accent  # Warning state
            else:
                pen_color = self.color_neon
                
            pen_active = QPen(pen_color, 5)
            pen_active.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_active)
            
            # Draw arc. Start at top (90 degrees). Arcs in Qt are 1/16th of a degree.
            # Angle increases counter-clockwise, so negative span draws clockwise.
            span_angle = -int((val / 100.0) * 360.0 * 16.0)
            painter.drawArc(QRectF(cx - r, cy - r, r * 2, r * 2), 90 * 16, span_angle)
            
            # 3. Draw central text labels
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(QRectF(cx - r, cy - r + 3, r * 2, r * 2), 
                             Qt.AlignmentFlag.AlignCenter, f"{display_label}\n{display_text}")
            
            # Draw micro outer bracket marks for high-tech HUD look
            pen_bracket = QPen(QColor(0, 210, 211, 60), 1)
            painter.setPen(pen_bracket)
            b_r = r + 8
            painter.drawArc(QRectF(cx - b_r, cy - b_r, b_r * 2, b_r * 2), 45 * 16, 90 * 16)
            painter.drawArc(QRectF(cx - b_r, cy - b_r, b_r * 2, b_r * 2), 225 * 16, 90 * 16)
