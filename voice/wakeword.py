import time
import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal
from config import PIVOTECH_ACCESS_KEY, WAKE_WORDS

try:
    import pvporcupine
    import pyaudio
    import struct
    HAS_PICOVOICE = True
except ImportError:
    HAS_PICOVOICE = False

class WakeWordDetectorThread(QThread):
    """Background listener checking for the wake word ('Hey Jarvis' or 'Jarvis')."""
    
    wake_word_detected = pyqtSignal()
    status_changed = pyqtSignal(str) # 'listening', 'stopped', 'error'
    
    def __init__(self, pv_key=PIVOTECH_ACCESS_KEY, wake_words=WAKE_WORDS):
        super().__init__()
        self.pv_key = pv_key
        self.wake_words = [w.lower() for w in wake_words]
        self.is_running = False

    def run(self):
        self.is_running = True
        
        # Method 1: Try Picovoice Porcupine (Fast, offline, low CPU)
        if HAS_PICOVOICE and self.pv_key:
            try:
                self._run_porcupine()
                return
            except Exception as e:
                print(f"[Wakeword] Picovoice failed: {e}. Falling back to SpeechRecognition.")
        
        # Method 2: SpeechRecognition fallback (Internet needed, slightly slower but works free)
        self._run_fallback_recognizer()

    def _run_porcupine(self):
        """Runs wake word detection using Picovoice Porcupine."""
        self.status_changed.emit("listening")
        
        # Look for 'jarvis' keyword
        porcupine = pvporcupine.create(
            access_key=self.pv_key,
            keywords=['jarvis']
        )
        
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )
        
        print("[Wakeword] Picovoice Porcupine listening for 'Jarvis'...")
        
        while self.is_running:
            try:
                pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
                
                keyword_index = porcupine.process(pcm)
                if keyword_index >= 0:
                    print("[Wakeword] Wake word detected via Porcupine!")
                    self.wake_word_detected.emit()
                    # Sleep briefly to avoid double trigger
                    self.msleep(1500)
            except Exception as e:
                print(f"[Wakeword] Error in Porcupine loop: {e}")
                self.msleep(100)
                
        # Clean up
        audio_stream.close()
        pa.terminate()
        porcupine.delete()
        self.status_changed.emit("stopped")

    def _run_fallback_recognizer(self):
        """Continuous low-overhead listening fallback using Google speech recognizer."""
        self.status_changed.emit("listening")
        
        r = sr.Recognizer()
        r.energy_threshold = 250
        r.dynamic_energy_threshold = True
        
        try:
            mic = sr.Microphone()
        except Exception as e:
            print(f"[Wakeword] Fallback mic error: {e}")
            self.status_changed.emit("error")
            return
            
        print("[Wakeword] Fallback listener listening for wake word...")
        
        while self.is_running:
            try:
                with mic as source:
                    # Capture a short 3 second audio clip to analyze
                    # Using small phase limits keeps it snappy and low CPU
                    audio = r.listen(source, timeout=3, phrase_time_limit=3)
                
                # Fast local recognize (using English)
                text = r.recognize_google(audio, language="en-US").lower()
                print(f"[Wakeword] Checking: '{text}'")
                
                # Check if wake word in spoken text
                if any(word in text for word in self.wake_words):
                    print("[Wakeword] Wake word detected via fallback SpeechRecognition!")
                    self.wake_word_detected.emit()
                    self.msleep(2000)
                    
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                # Log other errors and retry
                print(f"[Wakeword] Fallback error: {e}")
                self.msleep(500)
                
        self.status_changed.emit("stopped")

    def stop(self):
        """Stops the wakeword listener."""
        self.is_running = False
        self.terminate()
        self.wait()
