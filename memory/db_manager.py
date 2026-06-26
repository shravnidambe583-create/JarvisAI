import os
import sqlite3
from datetime import datetime
from config import DATABASE_PATH

class DatabaseManager:
    """Manages SQLite database for JARVIS X."""
    
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def _get_connection(self):
        """Get a fresh database connection (thread-safe on-demand connection)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize the database tables if they do not exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Conversations Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                mood TEXT
            )
        ''')
        
        # User Preferences Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                pref_key TEXT PRIMARY KEY,
                pref_value TEXT NOT NULL
            )
        ''')
        
        # Tasks & Missions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mission_name TEXT,
                task_desc TEXT NOT NULL,
                deadline TEXT,
                status TEXT DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Memory Vault Table (encrypted storage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                encrypted_payload TEXT NOT NULL,
                category TEXT DEFAULT 'note',
                created_at TEXT NOT NULL
            )
        ''')
        
        # Command History Table (for habits & command prediction)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()

    # --- Conversation Logging ---
    def save_message(self, role, message, mood=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO conversations (timestamp, role, message, mood) VALUES (?, ?, ?, ?)",
            (timestamp, role, message, mood)
        )
        conn.commit()
        conn.close()

    def get_conversation_history(self, limit=50):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, role, message, mood FROM conversations ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        # Return in chronological order
        return [dict(row) for row in reversed(rows)]

    def clear_conversation_history(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM conversations")
        conn.commit()
        conn.close()

    # --- User Preferences ---
    def set_preference(self, key, value):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_preferences (pref_key, pref_value) VALUES (?, ?)",
            (key, str(value))
        )
        conn.commit()
        conn.close()

    def get_preference(self, key, default=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT pref_value FROM user_preferences WHERE pref_key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default

    # --- Mission and Tasks System ---
    def add_task(self, task_desc, mission_name=None, deadline=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO tasks_missions (mission_name, task_desc, deadline, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
            (mission_name, task_desc, deadline, created_at)
        )
        conn.commit()
        conn.close()

    def get_tasks(self, mission_name=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if mission_name:
            cursor.execute(
                "SELECT id, mission_name, task_desc, deadline, status, progress, created_at FROM tasks_missions WHERE mission_name = ?",
                (mission_name,)
            )
        else:
            cursor.execute("SELECT id, mission_name, task_desc, deadline, status, progress, created_at FROM tasks_missions")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_task_status(self, task_id, status, progress=0):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks_missions SET status = ?, progress = ? WHERE id = ?",
            (status, progress, task_id)
        )
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks_missions WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    # --- Memory Vault ---
    def save_vault_item(self, title, encrypted_payload, category='note'):
        conn = self._get_connection()
        cursor = conn.cursor()
        created_at = datetime.now().isoformat()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO memory_vault (title, encrypted_payload, category, created_at) VALUES (?, ?, ?, ?)",
                (title, encrypted_payload, category, created_at)
            )
            conn.commit()
            success = True
        except sqlite3.Error:
            success = False
        conn.close()
        return success

    def get_vault_items(self, category=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT title, encrypted_payload, category, created_at FROM memory_vault WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT title, encrypted_payload, category, created_at FROM memory_vault")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_vault_item(self, title):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory_vault WHERE title = ?", (title,))
        conn.commit()
        conn.close()

    # --- Command Habits & Predictions ---
    def log_command(self, command):
        conn = self._get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute("INSERT INTO command_history (command, timestamp) VALUES (?, ?)", (command, timestamp))
        conn.commit()
        conn.close()

    def get_recent_commands(self, limit=10):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT command, COUNT(command) as cnt FROM command_history GROUP BY command ORDER BY cnt DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [row['command'] for row in rows]
