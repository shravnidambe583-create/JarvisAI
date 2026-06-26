import os
import time
import base64
from PIL import Image
import mss

# Optional OCR library imports
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

from config import SCREENSHOT_DIR, OPENAI_API_KEY
from openai import OpenAI

class ScreenIntelligence:
    """Manages screenshot captures, OCR text extraction, and GPT-4o-Vision screen analysis."""
    
    def __init__(self, screenshot_dir=SCREENSHOT_DIR):
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.ocr_reader = None
        
        # Initialize EasyOCR reader if available (cached local loading)
        if HAS_EASYOCR:
            try:
                # Load English reader
                self.ocr_reader = easyocr.Reader(['en'], gpu=False)
            except Exception as e:
                print(f"[ScreenIntel] Failed to init EasyOCR: {e}")

    def capture_screen(self) -> str:
        """Captures the current desktop screen and saves it. Returns file path."""
        timestamp = int(time.time())
        file_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
        
        print(f"[ScreenIntel] Capturing screenshot to {file_path}...")
        with mss.mss() as sct:
            # Capture full screen
            monitor = sct.monitors[1]  # Primary monitor
            sct_img = sct.grab(monitor)
            # Save to png
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=file_path)
            
        return file_path

    def extract_text(self, image_path: str) -> str:
        """Extracts text content from the image file via Tesseract or EasyOCR fallbacks."""
        if not os.path.exists(image_path):
            return "Image path does not exist."
            
        print("[ScreenIntel] Extracting text (OCR)...")
        
        # Method 1: Tesseract OCR
        if HAS_TESSERACT:
            try:
                text = pytesseract.image_to_string(Image.open(image_path))
                if text.strip():
                    return text
            except Exception as e:
                print(f"[ScreenIntel] Tesseract OCR error: {e}")
                
        # Method 2: EasyOCR
        if HAS_EASYOCR and self.ocr_reader:
            try:
                results = self.ocr_reader.readtext(image_path)
                text = " ".join([res[1] for res in results])
                if text.strip():
                    return text
            except Exception as e:
                print(f"[ScreenIntel] EasyOCR error: {e}")
                
        # Default mock fallback if no OCR library works
        return "[OCR Error: No working OCR engines (Tesseract/EasyOCR) found or image has no readable text.]"

    def analyze_screen_with_gpt(self, image_path: str, user_prompt: str = "Explain what is on my screen.") -> str:
        """Sends the screenshot to GPT-4o-Vision for full analysis and description."""
        if not OPENAI_API_KEY:
            # Local fallback summary using OCR
            ocr_text = self.extract_text(image_path)
            if "OCR Error" not in ocr_text and ocr_text.strip():
                return f"[Local Offline Analysis]: I captured your screen and extracted the following text: \n\n\"{ocr_text[:300]}...\". Let me know if you want me to perform specific automations on these elements."
            return "I captured your screen, but I cannot perform advanced visual intelligence without an OPENAI_API_KEY. However, the screenshot is saved in your screenshots directory."
            
        print("[ScreenIntel] Sending screen to GPT Vision...")
        try:
            # Encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"You are JARVIS X, a smart desktop AI assistant. Analyze this desktop screenshot and answer the user query: '{user_prompt}'. Keep your response brief, informative, and professional like JARVIS."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            analysis = response.choices[0].message.content
            return analysis
        except Exception as e:
            return f"Error during GPT-Vision screen analysis: {e}"
