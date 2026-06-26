import os
import random
import shutil
from manager import BasePlugin

class SystemDiagnosticsPlugin(BasePlugin):
    """An example JARVIS X plugin adding diagnostics commands."""
    
    name = "SystemDiagnosticsPlugin"
    description = "Provides extra storage space diagnostics and coin flip functions."
    version = "1.0.0"

    def get_commands(self):
        """Map voice trigger phrases to execution callbacks."""
        return {
            "check storage": self.check_storage,
            "flip a coin": self.flip_coin,
            "diagnostic scan": self.diagnostic_scan
        }

    def check_storage(self, query: str) -> str:
        """Determines disk space usage on the primary drive."""
        total, used, free = shutil.disk_usage("/")
        gb = 1024 * 1024 * 1024
        return f"Primary storage status: Total capacity is {total/gb:.1f} Gigabytes. Currently using {used/gb:.1f} Gigabytes, with {free/gb:.1f} Gigabytes remaining."

    def flip_coin(self, query: str) -> str:
        """Returns random Heads or Tails result."""
        result = random.choice(["Heads", "Tails"])
        return f"I have flipped a virtual coin. The result is {result}."

    def diagnostic_scan(self, query: str) -> str:
        """Simulates an advanced diagnostics scan of system files."""
        # Simple simulated scan
        env_vars = len(os.environ)
        return f"Running diagnostics. Core memory registers nominal. Custom environment variables active: {env_vars}. Security firewalls active. All systems functional."
