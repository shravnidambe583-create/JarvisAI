import os
import cv2
import time
import numpy as np
from config import FACE_DATA_DIR, FACE_RECOGNITION_TOLERANCE

try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False

class FaceLogin:
    """Manages dlib-free/fallback-enabled Face Recognition authentication & intruder alert."""
    
    def __init__(self, data_dir=FACE_DATA_DIR):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_names = []
        self.known_encodings = []  # For face_recognition library
        self.known_images = []     # For template/histogram fallback matching
        
        self.load_registered_faces()

    def is_available(self) -> bool:
        """Returns True if a camera is connected."""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
        available = cap.isOpened()
        cap.release()
        return available

    def load_registered_faces(self):
        """Loads face signatures from the registered faces directory."""
        self.known_names = []
        self.known_encodings = []
        self.known_images = []
        
        if not os.path.exists(self.data_dir):
            return
            
        for file in os.listdir(self.data_dir):
            if file.endswith(('.jpg', '.png', '.jpeg')):
                name = os.path.splitext(file)[0]
                img_path = os.path.join(self.data_dir, file)
                img = cv2.imread(img_path)
                
                if img is None:
                    continue
                    
                self.known_names.append(name)
                
                # Method 1: Load for face_recognition library
                if HAS_FACE_RECOGNITION:
                    try:
                        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        encs = face_recognition.face_encodings(rgb_img)
                        if encs:
                            self.known_encodings.append(encs[0])
                        else:
                            self.known_encodings.append(None)
                    except Exception:
                        self.known_encodings.append(None)
                
                # Method 2: Load for fallback matching (histogram/template)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_roi = gray[y:y+h, x:x+w]
                    face_roi_resized = cv2.resize(face_roi, (128, 128))
                    self.known_images.append(face_roi_resized)
                else:
                    # Fallback to whole resized image
                    self.known_images.append(cv2.resize(gray, (128, 128)))

    def register_face(self, name: str) -> bool:
        """Captures a frame from webcam, extracts face, and saves as registered user."""
        print(f"[FaceAuth] Registering face for '{name}'...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
        
        if not cap.isOpened():
            print("[FaceAuth] Error: Camera not accessible.")
            return False
            
        face_captured = False
        start_time = time.time()
        
        while time.time() - start_time < 10:  # Timeout after 10 seconds
            ret, frame = cap.read()
            if not ret:
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Draw overlay on camera preview
            preview = frame.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(preview, (x, y), (x+w, y+h), (0, 210, 211), 2)
                cv2.putText(preview, "Hold Still - Capturing", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 210, 211), 2)
                            
            cv2.imshow("JARVIS X - Register Face", preview)
            
            if len(faces) > 0 and not face_captured:
                # Save the face region
                img_path = os.path.join(self.data_dir, f"{name}.jpg")
                cv2.imwrite(img_path, frame)
                print(f"[FaceAuth] Face image saved to {img_path}")
                face_captured = True
                break
                
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        self.load_registered_faces()
        return face_captured

    def authenticate(self) -> bool:
        """Authenticates user using face recognition. Returns True if matched."""
        if not self.known_names:
            print("[FaceAuth] No registered users available. Bypassing auth.")
            return True
            
        print("[FaceAuth] Initiating face authentication scan...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
        
        if not cap.isOpened():
            print("[FaceAuth] Camera not accessible. Authentication bypassed.")
            return True
            
        authenticated = False
        start_time = time.time()
        intruder_detected = False
        
        while time.time() - start_time < 8:  # 8-second scan duration
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Draw holographic target locks in UI
            preview = frame.copy()
            h, w, _ = preview.shape
            
            # Futuristic targeting box
            cv2.rectangle(preview, (int(w/4), int(h/4)), (int(3*w/4), int(3*h/4)), (233, 69, 96), 1)
            cv2.putText(preview, "JARVIS SYSTEM SECURE LOGIN", (20, 30), 
                        cv2.FONT_HERSHEY_MONO, 0.5, (0, 210, 211), 1)
                        
            # Detect faces
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w_f, h_f) in faces:
                cv2.rectangle(preview, (x, y), (x+w_f, y+h_f), (0, 210, 211), 2)
                
                matched_name = "Unknown"
                
                # Method 1: Use face_recognition library if available
                if HAS_FACE_RECOGNITION and len(self.known_encodings) > 0:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face_encs = face_recognition.face_encodings(rgb_frame, [(y, x+w_f, y+h_f, x)])
                    
                    if face_encs:
                        matches = face_recognition.compare_faces(self.known_encodings, face_encs[0], tolerance=FACE_RECOGNITION_TOLERANCE)
                        if True in matches:
                            first_match_idx = matches.index(True)
                            matched_name = self.known_names[first_match_idx]
                
                # Method 2: Fallback template matching (pixel diff of resized gray face)
                if matched_name == "Unknown" and len(self.known_images) > 0:
                    face_roi = gray[y:y+h_f, x:x+w_f]
                    face_roi_resized = cv2.resize(face_roi, (128, 128))
                    
                    best_score = float('inf')
                    best_idx = -1
                    
                    for idx, known_img in enumerate(self.known_images):
                        # Calculate Mean Square Error (MSE)
                        err = np.sum((face_roi_resized.astype("float") - known_img.astype("float")) ** 2)
                        err /= float(face_roi_resized.shape[0] * face_roi_resized.shape[1])
                        
                        if err < best_score:
                            best_score = err
                            best_idx = idx
                            
                    # Empirically, MSE < 6000 indicates a very close pixel match on grayscale normalized heads
                    if best_score < 6000 and best_idx != -1:
                        matched_name = self.known_names[best_idx]
                
                if matched_name != "Unknown":
                    cv2.putText(preview, f"Lock Verified: {matched_name}", (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 210, 211), 2)
                    authenticated = True
                    break
                else:
                    cv2.putText(preview, "Access Denied", (x, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (233, 69, 96), 2)
                    intruder_detected = True
            
            cv2.imshow("JARVIS X - Security Authentication", preview)
            
            if authenticated:
                break
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        
        if not authenticated and intruder_detected:
            print("[FaceAuth] ⚠️ INTRUDER WARNING: Access violation recorded.")
            self.trigger_intruder_alert()
            
        return authenticated

    def trigger_intruder_alert(self):
        """Intruder detection routine. Capture image of intruder and sound alert."""
        try:
            # Sound alert (Beep sound using Windows api)
            import winsound
            winsound.Beep(1000, 1500) # 1000 Hz for 1.5s
        except Exception:
            pass
        
        # Capture photo of intruder
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                intruder_path = os.path.join(self.data_dir, "intruder_snapshot.jpg")
                cv2.imwrite(intruder_path, frame)
                print(f"[FaceAuth] Intruder snapshot saved to {intruder_path}")
            cap.release()
