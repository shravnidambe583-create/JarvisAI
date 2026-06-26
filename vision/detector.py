import cv2
import os
import numpy as np

class AIDetector:
    """Manages Object Detection, Face Tracking, and Emotion Recognition via OpenCV."""
    
    def __init__(self):
        # Load Haar Cascades for face, eyes, and smile detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Paths for MobileNetSSD Object Detection
        self.net = None
        self.classes = [
            "background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"
        ]
        
        # We try to initialize DNN Object detector if weights can be loaded
        # The MobileNetSSD model uses a prototxt and caffemodel
        self.proto_path = "database/MobileNetSSD_deploy.prototxt"
        self.model_path = "database/MobileNetSSD_deploy.caffemodel"
        
        # In a real environment, we'll try to load, or download if missing
        if os.path.exists(self.proto_path) and os.path.exists(self.model_path):
            try:
                self.net = cv2.dnn.readNetFromCaffe(self.proto_path, self.model_path)
            except Exception as e:
                print(f"[Detector] Failed to load Caffe DNN model: {e}")

    def detect_objects_and_faces(self, frame) -> tuple:
        """
        Analyzes a single frame from webcam.
        Returns:
            processed_frame: Image with overlays.
            metadata: dict of detections (objects list, count, detected emotions).
        """
        h_f, w_f, _ = frame.shape
        metadata = {
            "objects": [],
            "emotions": "Focused",
            "faces_count": 0
        }
        
        # Grayscale for Haar cascades
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Face & Emotion Recognition
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        metadata["faces_count"] = len(faces)
        
        for (x, y, w, h) in faces:
            # Draw Face Lock
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 210, 211), 2)
            cv2.putText(frame, "TARGET LOCK: HUMAN", (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 210, 211), 1)
            
            # ROI for face features
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            
            # Rule-based Emotion Recognition
            smile_detected = False
            smiles = self.smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
            if len(smiles) > 0:
                smile_detected = True
                
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 10)
            
            # Classify emotion
            if smile_detected:
                emotion = "Happy / Amused"
            elif len(eyes) > 2:
                emotion = "Surprised / Excited"
            elif len(eyes) == 0:
                emotion = "Sleepy / Pensive"
            else:
                emotion = "Focused / Neutral"
                
            metadata["emotions"] = emotion
            cv2.putText(frame, f"EMOTION: {emotion}", (x, y+h+20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (241, 196, 15), 1)
                        
            # Draw eye targets
            for (ex, ey, ew, eh) in eyes:
                cv2.circle(roi_color, (int(ex + ew/2), int(ey + eh/2)), int(ew/2), (0, 210, 211), 1)

        # 2. DNN Object Detection (if loaded)
        if self.net:
            try:
                # Resize to 300x300 and normalize for MobileNetSSD
                blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
                self.net.setInput(blob)
                detections = self.net.forward()
                
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    
                    if confidence > 0.4: # Filter by confidence
                        class_idx = int(detections[0, 0, i, 1])
                        class_name = self.classes[class_idx]
                        
                        # Calculate box coords
                        box = detections[0, 0, i, 3:7] * np.array([w_f, h_f, w_f, h_f])
                        (startX, startY, endX, endY) = box.astype("int")
                        
                        # Avoid duplicating face labels if person detected
                        if class_name == "person":
                            metadata["objects"].append("Person")
                            continue
                            
                        metadata["objects"].append(class_name.capitalize())
                        
                        # Draw box and label
                        cv2.rectangle(frame, (startX, startY), (endX, endY), (233, 69, 96), 1)
                        label = f"{class_name.capitalize()}: {int(confidence * 100)}%"
                        cv2.putText(frame, label, (startX, startY - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (233, 69, 96), 1)
            except Exception as e:
                print(f"[Detector] DNN forward pass error: {e}")
        else:
            # Fallback label in frame if DNN weights are missing
            cv2.putText(frame, "DNN DETECTOR: OFFLINE (Run setup.bat)", (10, h_f - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 100, 150), 1)
                        
        return frame, metadata

    def run_realtime_vision_scan(self) -> None:
        """Launches a full window preview showing live object detection and emotion tracking."""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY)
        
        if not cap.isOpened():
            print("[Detector] Camera not accessible.")
            return
            
        print("[Detector] Launching live vision scanning window. Press 'Q' to exit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            processed, metadata = self.detect_objects_and_faces(frame)
            
            # Top-left HUD diagnostics overlay
            cv2.putText(processed, f"JARVIS X VISION GRID | ACTIVE OBJECTS: {len(metadata['objects'])}", (20, 30), 
                        cv2.FONT_HERSHEY_MONO, 0.5, (0, 210, 211), 1)
            
            cv2.imshow("JARVIS X - Real-time AI Vision Scanner", processed)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
