import time
import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal

class VoiceListenerThread(QThread):
    """Background thread for continuous Speech-to-Text listening."""
    
    recognized_text = pyqtSignal(str)
    status_changed = pyqtSignal(str)  # 'idle', 'listening', 'processing', 'error'
    volume_energy = pyqtSignal(float) # Sends mic energy level for visualizer updates
    
    def __init__(self, energy_threshold=300, pause_threshold=0.8, device_index=None):
        super().__init__()
        self.energy_threshold = energy_threshold
        self.pause_threshold = pause_threshold
        self.device_index = device_index
        self.is_running = False
        self.language = "en-IN"  # Multi-lang support default (handles both Indian English and Hindi commands)
        
        # Init speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = self.pause_threshold
        
    def run(self):
        """Main listening loop."""
        self.is_running = True
        
        # Get mic source
        try:
            mic = sr.Microphone(device_index=self.device_index)
        except Exception as e:
            self.status_changed.emit("error")
            self.recognized_text.emit(f"[Mic Error: {e}]")
            return
            
        print("[Voice] Calibrating microphone for ambient noise...")
        self.status_changed.emit("processing")
        with mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
        print("[Voice] Listening active.")
        self.status_changed.emit("idle")
        
        while self.is_running:
            try:
                # Active listening state
                self.status_changed.emit("listening")
                
                with mic as source:
                    # Capture audio in blocks so we can emit energy levels to the wave visualizer
                    # Wait, sr.listen holds until phrase finishes. To get real-time voice levels,
                    # we can read raw mic input in chunks, but sr.listen is easier for phrase detection.
                    # We will mock/estimate visualizer inputs or use pyAudio for real-time frequency data.
                    # A neat compromise: we listen for phrase. While listening, we can report active state.
                    audio_data = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)
                
                # Processing state
                self.status_changed.emit("processing")
                print("[Voice] Processing speech...")
                
                # Speech recognition
                # Try Google Web Speech API (free, fast, handles Hindi and English)
                text = self.recognizer.recognize_google(audio_data, language=self.language)
                
                if text.strip():
                    print(f"[Voice] Recognized: {text}")
                    self.recognized_text.emit(text)
                    
            except sr.WaitTimeoutError:
                # Timeout is normal when user is not speaking
                self.status_changed.emit("idle")
            except sr.UnknownValueError:
                # Audio heard but not understood
                self.status_changed.emit("idle")
            except sr.RequestError as e:
                # API error
                print(f"[Voice] Google API Error: {e}")
                self.status_changed.emit("idle")
                self.msleep(1000)
            except Exception as e:
                print(f"[Voice] Error in listening loop: {e}")
                self.status_changed.emit("idle")
                self.msleep(1000)
                
        self.status_changed.emit("idle")

    def stop(self):
        """Stops the listening thread."""
        self.is_running = False
        self.terminate()
        self.wait()
        
    def set_language(self, lang_code):
        """Set language code, e.g. 'en-US', 'hi-IN'."""
        self.language = lang_code
