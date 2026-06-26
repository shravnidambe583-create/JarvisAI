import os
import sys
import asyncio
import threading
import tempfile
import pyttsx3
from PyQt6.QtCore import QObject, pyqtSignal

# Optional edge-tts import
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

class TTSSignals(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(str)

class SpeakEngine:
    """Manages Text-to-Speech synthesis with edge-tts and pyttsx3 fallback."""
    
    def __init__(self, rate=180, volume=1.0, voice_index=0):
        self.rate = rate
        self.volume = volume
        self.voice_index = voice_index
        self.signals = TTSSignals()
        self._is_speaking = False
        
        # Initialize pyttsx3 fallback
        try:
            self.pyttsx_engine = pyttsx3.init()
            self.pyttsx_engine.setProperty('rate', self.rate)
            self.pyttsx_engine.setProperty('volume', self.volume)
            self.voices = self.pyttsx_engine.getProperty('voices')
            if self.voices:
                idx = min(self.voice_index, len(self.voices) - 1)
                self.pyttsx_engine.setProperty('voice', self.voices[idx].id)
        except Exception as e:
            print(f"[TTS] Warning: Failed to init pyttsx3: {e}")
            self.pyttsx_engine = None

    def speak(self, text, lang='en'):
        """Speak text in a non-blocking background thread."""
        if not text:
            return
        
        self._is_speaking = True
        self.signals.started.emit()
        
        # Run speech synthesis in a background thread to prevent GUI freezing
        threading.Thread(target=self._run_speech, args=(text, lang), daemon=True).start()

    def _run_speech(self, text, lang):
        try:
            # Check language and map to edge-tts voice
            # hi = Hindi, en = English
            if lang == 'hi':
                voice_name = "hi-IN-MadhurNeural"  # Hindi natural male
            else:
                voice_name = "en-US-GuyNeural"     # English natural male (Jarvis-like)

            success = False
            if HAS_EDGE_TTS:
                try:
                    success = self._speak_edge_tts(text, voice_name)
                except Exception as e:
                    print(f"[TTS] edge-tts execution failed, falling back: {e}")
            
            if not success:
                self._speak_pyttsx3(text, lang)
                
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self._is_speaking = False
            self.signals.finished.emit()

    def _speak_edge_tts(self, text, voice_name) -> bool:
        """Synthesize using edge-tts and play it using windows native player/start or PyQt."""
        try:
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "jarvis_speech.mp3")
            
            # Remove old speech file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
            
            # Async generate MP3
            async def generate():
                communicate = edge_tts.Communicate(text, voice_name)
                await communicate.save(temp_file)
                
            asyncio.run(generate())
            
            # Play MP3
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                if sys.platform == "win32":
                    # Non-blocking play on windows using command-line command or standard utility
                    # We can use powershell to play it:
                    # command = f'powershell -c "$m = New-Object System.Windows.Media.MediaPlayer; $m.Open(\'{temp_file}\'); $m.Play(); Start-Sleep -s [Math]::Ceiling($m.NaturalDuration.TimeSpan.TotalSeconds + 1)"'
                    # Wait, System.Windows.Media requires presentationcore. Let's do a simpler method:
                    # Use windows media player launch or ctypes to play
                    import ctypes
                    winmm = ctypes.windll.winmm
                    winmm.mciSendStringW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
                    winmm.mciSendStringW.restype = ctypes.c_uint
                    
                    winmm.mciSendStringW(f'open "{temp_file}" type mpegvideo alias jarvis_speech', None, 0, 0)
                    winmm.mciSendStringW('play jarvis_speech wait', None, 0, 0)
                    winmm.mciSendStringW('close jarvis_speech', None, 0, 0)
                else:
                    # Linux/macOS
                    player = "afplay" if sys.platform == "darwin" else "play"
                    os.system(f"{player} {temp_file} >/dev/null 2>&1")
                return True
        except Exception as e:
            print(f"[TTS] edge-tts error: {e}")
        return False

    def _speak_pyttsx3(self, text, lang):
        """Synthesize using offline pyttsx3."""
        if not self.pyttsx_engine:
            return
            
        try:
            # Change voice depending on language if available
            if lang == 'hi' and len(self.voices) > 1:
                # Find a Hindi voice or use secondary
                self.pyttsx_engine.setProperty('voice', self.voices[1].id)
            else:
                if self.voices:
                    idx = min(self.voice_index, len(self.voices) - 1)
                    self.pyttsx_engine.setProperty('voice', self.voices[idx].id)
            
            self.pyttsx_engine.say(text)
            self.pyttsx_engine.runAndWait()
        except Exception as e:
            print(f"[TTS] pyttsx3 speech failed: {e}")
            # Last resort print
            print(f"JARVIS: {text}")

    def stop(self):
        """Stop current speech."""
        if sys.platform == "win32":
            import ctypes
            winmm = ctypes.windll.winmm
            winmm.mciSendStringW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_void_p]
            winmm.mciSendStringW.restype = ctypes.c_uint
            
            winmm.mciSendStringW('stop jarvis_speech', None, 0, 0)
            winmm.mciSendStringW('close jarvis_speech', None, 0, 0)
            
        if self.pyttsx_engine:
            try:
                self.pyttsx_engine.stop()
            except Exception:
                pass
        self._is_speaking = False
        self.signals.finished.emit()
