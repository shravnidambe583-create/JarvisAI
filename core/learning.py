import json
from datetime import datetime
from memory.db_manager import DatabaseManager

class LearningSystem:
    """Manages command habit predictions, user preferences, and custom shortcuts."""
    
    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()
        self._load_shortcuts()

    def _load_shortcuts(self):
        """Loads registered shortcuts from preferences."""
        shortcuts_json = self.db.get_preference("voice_shortcuts", "{}")
        try:
            self.shortcuts = json.loads(shortcuts_json)
        except Exception:
            self.shortcuts = {}

    def save_shortcut(self, voice_trigger: str, action_command: str) -> None:
        """Saves a custom voice shortcut to execute a system command or application launch."""
        trigger = voice_trigger.lower().strip()
        self.shortcuts[trigger] = action_command
        self.db.set_preference("voice_shortcuts", json.dumps(self.shortcuts))
        print(f"[Learning] Saved shortcut: '{trigger}' -> '{action_command}'")

    def get_shortcut_action(self, voice_phrase: str) -> str:
        """Returns the system command mapping if the voice phrase matches a shortcut."""
        phrase = voice_phrase.lower().strip()
        for trigger, action in self.shortcuts.items():
            if trigger in phrase:
                print(f"[Learning] Shortcut triggered: '{trigger}' mapping to '{action}'")
                return action
        return None

    def delete_shortcut(self, voice_trigger: str) -> bool:
        """Deletes a custom shortcut."""
        trigger = voice_trigger.lower().strip()
        if trigger in self.shortcuts:
            del self.shortcuts[trigger]
            self.db.set_preference("voice_shortcuts", json.dumps(self.shortcuts))
            return True
        return False

    def predict_next_command(self) -> list:
        """
        Analyzes command history in SQLite and suggests the top 3 commands
        most likely to be executed during the current time of day.
        """
        current_hour = datetime.now().hour
        
        # We classify hours:
        # Morning (6-11), Study/Work (12-17), Evening/Night (18-23), Late Night (0-5)
        if 6 <= current_hour < 12:
            time_slot = "morning"
        elif 12 <= current_hour < 18:
            time_slot = "study_work"
        elif 18 <= current_hour < 24:
            time_slot = "evening_night"
        else:
            time_slot = "late_night"
            
        print(f"[Learning] Current slot: {time_slot} (hour {current_hour})")
        
        # Fetch command logs from SQLite
        conn = self.db._get_connection()
        cursor = conn.cursor()
        
        # We look for command counts in command history table
        cursor.execute("SELECT command, timestamp FROM command_history")
        rows = cursor.fetchall()
        conn.close()
        
        slot_commands = []
        for row in rows:
            cmd = row["command"]
            ts_str = row["timestamp"]
            try:
                dt = datetime.fromisoformat(ts_str)
                hour = dt.hour
                
                # Check if this log matches the current time slot
                if 6 <= hour < 12:
                    log_slot = "morning"
                elif 12 <= hour < 18:
                    log_slot = "study_work"
                elif 18 <= hour < 24:
                    log_slot = "evening_night"
                else:
                    log_slot = "late_night"
                    
                if log_slot == time_slot:
                    slot_commands.append(cmd)
            except Exception:
                pass
                
        # Count frequency of commands in current slot
        freq = {}
        for cmd in slot_commands:
            freq[cmd] = freq.get(cmd, 0) + 1
            
        # Sort by frequency descending
        sorted_cmds = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)
        suggestions = sorted_cmds[:3]
        
        # If no history is found, populate with smart defaults based on the slot
        if not suggestions:
            defaults = {
                "morning": ["Open Chrome", "Show Calendar", "Weather Report"],
                "study_work": ["Open VS Code", "Create Mission", "Check System Status"],
                "evening_night": ["Play Music", "Show Reminders", "Lock Computer"],
                "late_night": ["Lock Computer", "Shutdown PC", "Explain Screen"]
            }
            suggestions = defaults[time_slot]
            
        return suggestions
