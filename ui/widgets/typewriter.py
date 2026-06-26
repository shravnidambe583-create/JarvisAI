from PyQt6.QtWidgets import QTextBrowser
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QTextCursor

class TypewriterLabel(QTextBrowser):
    """Custom terminal text display scrolling character-by-character with neon styling."""
    
    typing_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_html = ""
        self.current_char_idx = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.type_next_char)
        self.cursor_visible = True
        
        # Blink cursor timer
        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.toggle_cursor)
        self.blink_timer.start(500)
        
        # Apply strict sci-fi terminal styling
        self.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                border: none;
                font-family: "Courier New", Courier, monospace;
                font-size: 13px;
                color: #00d2d3;
            }
        """)

    def start_typing(self, html_text: str, delay_ms: int = 15):
        """Prepares text markup and launches typing timer."""
        # Stop existing run
        self.timer.stop()
        self.clear()
        
        # Parse plain-text length and keep html marks
        # For simplicity, we can strip html tags to count chars, 
        # but to display rich text we can construct incremental html.
        # A simple robust way to animate typewriter with HTML text:
        # We can extract text chunks, or simply strip tags and type plain text,
        # or type character-by-character of the raw HTML text (handles code blocks nicely).
        # Let's type step-by-step of the raw text. To avoid displaying broken HTML tags,
        # we will convert newlines to <br> and display character increments. If we display raw text increments,
        # it is extremely clean.
        
        # Convert newlines to HTML line breaks
        self.full_html = html_text.replace("\n", "<br>")
        self.current_char_idx = 0
        
        self.timer.start(delay_ms)

    def type_next_char(self):
        if self.current_char_idx <= len(self.full_html):
            # Check if we are inside an HTML tag, if so type the whole tag instantly
            # to avoid showing raw '<br>' or '<font>' codes in UI
            current_text = self.full_html[:self.current_char_idx]
            
            while self.current_char_idx < len(self.full_html) and self.full_html[self.current_char_idx] == '<':
                # Fast forward to closing '>'
                closing_idx = self.full_html.find('>', self.current_char_idx)
                if closing_idx != -1:
                    self.current_char_idx = closing_idx + 1
                    current_text = self.full_html[:self.current_char_idx]
                else:
                    break
                    
            cursor_suffix = " █" if self.cursor_visible else ""
            self.setHtml(current_text + cursor_suffix)
            
            # Scroll browser to bottom
            self.moveCursor(QTextCursor.MoveOperation.End)
            
            self.current_char_idx += 1
        else:
            self.timer.stop()
            self.setHtml(self.full_html)
            self.moveCursor(QTextCursor.MoveOperation.End)
            self.typing_finished.emit()

    def toggle_cursor(self):
        """Blinks the cursor block at the end of text when typing is finished or idle."""
        self.cursor_visible = not self.cursor_visible
        if not self.timer.isActive():
            # Apply cursor blink to complete text
            cursor_suffix = " █" if self.cursor_visible else ""
            self.setHtml(self.full_html + cursor_suffix)
            self.moveCursor(QTextCursor.MoveOperation.End)
