import unittest
import os
import tempfile
from unittest.mock import MagicMock
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.db_manager import DatabaseManager
from core.orchestrator import JarvisOrchestrator

class TestJarvisCore(unittest.TestCase):
    
    def setUp(self):
        # Create temp DB for testing
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        # Initialize database manager with temp path
        self.db = DatabaseManager(db_path=self.temp_db_path)
        # Initialize orchestrator with mocked DB
        self.orchestrator = JarvisOrchestrator(db=self.db)
        self.orchestrator.tts = MagicMock()
        self.orchestrator.system = MagicMock()
        self.orchestrator.apps = MagicMock()

    def patch_config(self):
        pass

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_math_code_execution(self):
        # Test evaluation sandboxing
        res = self.orchestrator._process_command_logic("Execute python 2 + 2")
        self.assertIn("[Result]: 4", res)

        res_math = self.orchestrator._process_command_logic("Execute python math.sqrt(16)")
        self.assertIn("[Result]: 4.0", res_math)

    def test_volume_commands(self):
        self.orchestrator._process_command_logic("Set volume to 75")
        self.orchestrator.system.set_volume.assert_called_with(75)

    def test_app_launch_commands(self):
        self.orchestrator._process_command_logic("Open chrome")
        self.orchestrator.apps.open_app.assert_called_with("chrome")

    def test_emergency_alert_command(self):
        self.orchestrator.email = MagicMock()
        self.orchestrator._process_command_logic("emergency alert")
        self.orchestrator.email.send_emergency_alert.assert_called()

if __name__ == "__main__":
    unittest.main()
