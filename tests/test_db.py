import unittest
import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.db_manager import DatabaseManager
from memory.vault import MemoryVault

class TestJarvisDatabase(unittest.TestCase):
    
    def setUp(self):
        # Create a temp database path for unit testing
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = DatabaseManager(db_path=self.temp_db_path)
        self.vault = MemoryVault(master_password="test_master_key")

    def tearDown(self):
        # Close temp file
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_preferences(self):
        self.db.set_preference("theme", "neon-blue")
        val = self.db.get_preference("theme")
        self.assertEqual(val, "neon-blue")
        
        # Test default fallback
        val_default = self.db.get_preference("volume", "80")
        self.assertEqual(val_default, "80")

    def test_conversations(self):
        self.db.save_message("user", "Hello Jarvis", mood="Calm")
        self.db.save_message("assistant", "Hello Sir. Ready to assist.")
        
        history = self.db.get_conversation_history(limit=5)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["message"], "Hello Jarvis")
        self.assertEqual(history[0]["mood"], "Calm")
        self.assertEqual(history[1]["role"], "assistant")

    def test_vault_encryption(self):
        secret = "super_secret_api_key_123"
        enc = self.vault.encrypt(secret)
        self.assertNotEqual(secret, enc)
        
        dec = self.vault.decrypt(enc)
        self.assertEqual(secret, dec)

    def test_tasks_missions(self):
        # Add task
        self.db.add_task("Code UI widgets", mission_name="Jarvis X")
        tasks = self.db.get_tasks(mission_name="Jarvis X")
        
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task_desc"], "Code UI widgets")
        self.assertEqual(tasks[0]["status"], "pending")
        
        # Update task status
        t_id = tasks[0]["id"]
        self.db.update_task_status(t_id, "completed", progress=100)
        
        tasks_updated = self.db.get_tasks(mission_name="Jarvis X")
        self.assertEqual(tasks_updated[0]["status"], "completed")
        self.assertEqual(tasks_updated[0]["progress"], 100)

if __name__ == "__main__":
    unittest.main()
