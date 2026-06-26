import os
import sys
import ctypes

# Try pycaw imports
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    HAS_PYCAW = True
except ImportError:
    HAS_PYCAW = False

# Try screen brightness control import
try:
    import screen_brightness_control as sbc
    HAS_SBC = True
except ImportError:
    HAS_SBC = False

class SystemController:
    """Manages system hardware automation: volume, brightness, power state."""
    
    def __init__(self):
        self.volume_interface = None
        if HAS_PYCAW and sys.platform == "win32":
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_interface = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
            except Exception as e:
                print(f"[SystemControl] Failed to initialize volume controls: {e}")

    def set_volume(self, level: int) -> bool:
        """Sets the system master volume (0 to 100)."""
        level = max(0, min(100, level))
        print(f"[SystemControl] Setting volume to {level}%")
        
        if self.volume_interface:
            try:
                # pycaw uses scalar level (0.0 to 1.0)
                self.volume_interface.SetMasterVolumeLevelScalar(level / 100.0, None)
                return True
            except Exception as e:
                print(f"[SystemControl] Pycaw failed to set volume: {e}")
        
        # Fallback using shell command on Windows
        if sys.platform == "win32":
            try:
                # Windows volume change can be triggered via keyboard simulation too,
                # but let's try calling powershell sound commands or sounder.exe if pycaw fails.
                # A fallback is simulating key presses using ctypes.
                # Keyboard code for Volume Up (0xAF) and Volume Down (0xAE).
                # Since we don't know the current level, a direct scalar set is better.
                # Let's write a powershell fallback:
                cmd = f'powershell -c "(Get-WmiObject -Query \'Select * from MSNdis_80211_ServiceAreaName\' -Namespace root/wmi).SetVolume({int(level * 655.35)})"'
                # This works on some systems, or using sound volume command.
                # If everything fails, report false.
                pass
            except Exception:
                pass
        return False

    def get_volume(self) -> int:
        """Gets current system master volume (0 to 100)."""
        if self.volume_interface:
            try:
                val = self.volume_interface.GetMasterVolumeLevelScalar()
                return int(val * 100)
            except Exception:
                pass
        return 50  # Default fallback

    def set_brightness(self, level: int) -> bool:
        """Sets system screen brightness (0 to 100)."""
        level = max(0, min(100, level))
        print(f"[SystemControl] Setting brightness to {level}%")
        
        if HAS_SBC:
            try:
                sbc.set_brightness(level)
                return True
            except Exception as e:
                print(f"[SystemControl] SBC failed to set brightness: {e}")
                
        # Windows PowerShell WMI fallback
        if sys.platform == "win32":
            try:
                cmd = f"powershell -c \"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})\""
                os.system(cmd)
                return True
            except Exception as e:
                print(f"[SystemControl] WMI brightness fallback failed: {e}")
        return False

    def get_brightness(self) -> int:
        """Gets current system brightness."""
        if HAS_SBC:
            try:
                val = sbc.get_brightness()
                if isinstance(val, list):
                    return val[0]
                return val
            except Exception:
                pass
        return 50  # Default fallback

    def lock_screen(self) -> bool:
        """Locks the user's desktop."""
        print("[SystemControl] Locking desktop screen...")
        if sys.platform == "win32":
            try:
                ctypes.windll.user32.LockWorkStation()
                return True
            except Exception as e:
                print(f"[SystemControl] Failed to lock workstation: {e}")
        else:
            # Linux lock fallback
            os.system("xdg-screensaver lock")
        return False

    def shutdown(self, force: bool = False) -> None:
        """Shutdown the computer."""
        print("[SystemControl] Shutting down computer...")
        if sys.platform == "win32":
            f_flag = "/f" if force else ""
            os.system(f"shutdown /s /t 5 {f_flag}")
        else:
            os.system("shutdown -h now")

    def restart(self, force: bool = False) -> None:
        """Restart the computer."""
        print("[SystemControl] Restarting computer...")
        if sys.platform == "win32":
            f_flag = "/f" if force else ""
            os.system(f"shutdown /r /t 5 {f_flag}")
        else:
            os.system("shutdown -r now")
            
    def sleep_pc(self) -> bool:
        """Puts computer in sleep/suspend mode."""
        print("[SystemControl] Suspending computer...")
        if sys.platform == "win32":
            # Call SetSuspendState
            # SetSuspendState(hibernate, force, disable_wake_events)
            try:
                ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
                return True
            except Exception as e:
                print(f"[SystemControl] Sleep command failed: {e}")
        else:
            os.system("systemctl suspend")
        return False
