import cv2
import mediapipe as mp
import requests
import json
import base64
from datetime import datetime

class FaceDetector:
    def __init__(self, server_url, min_detection_confidence=0.5, throttle_seconds=10):
        """
        Initialize the face detector
        
        Args:
            server_url (str): URL to send the face detection results
            min_detection_confidence (float): Minimum confidence threshold for detections
            throttle_seconds (int): Minimum seconds between server requests
        """
        self.server_url = server_url
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_draw = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=min_detection_confidence
        )
        self.last_sent_time = None
        self.throttle_seconds = throttle_seconds

    def should_send_request(self):
        """Check if enough time has passed since the last request"""
        if self.last_sent_time is None:
            return True
            
        time_diff = datetime.now() - self.last_sent_time
        return time_diff.total_seconds() >= self.throttle_seconds

    def process_frame(self, frame):
        """Process a single frame and detect faces"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_detection.process(rgb_frame)
        
        faces_data = []
        if results.detections:
            for detection in results.detections:
                # Get bounding box coordinates
                bbox = detection.location_data.relative_bounding_box
                h, w, c = frame.shape
                
                # Convert relative coordinates to absolute
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                # Draw rectangle around face
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                
                # Store face data
                faces_data.append({
                    'confidence': float(detection.score[0]),
                    'bbox': {
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height
                    }
                })
                
                # Draw detection confidence
                cv2.putText(frame, f'{int(detection.score[0] * 100)}%',
                          (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame, faces_data

    def send_to_server(self, frame, faces_data):
        """Send detection results to server if throttle time has passed"""
        if not self.should_send_request():
            return False
            
        try:
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Prepare data payload
            payload = {
                'timestamp': datetime.now().isoformat(),
                'image': img_base64,
                'faces': faces_data
            }
            
            # Send POST request with timeout
            response = requests.post(self.server_url, json=payload, timeout=2.0)
            if response.status_code == 200:
                self.last_sent_time = datetime.now()
                return True
            print(f"Server returned status code: {response.status_code}")
            return False
            
        except requests.exceptions.Timeout:
            print("Server request timed out")
            return False
        except requests.exceptions.ConnectionError:
            print("Connection error - server might be down")
            return False
        except Exception as e:
            print(f"Error sending data to server: {str(e)}")
            return False

def list_available_cameras():
    """List all available camera indices and their resolutions"""
    available_cameras = []
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                resolution = (
                    int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                )
                available_cameras.append((i, resolution))
            cap.release()
    return available_cameras

def main():
    # List available cameras
    cameras = list_available_cameras()
    if not cameras:
        print("No cameras found!")
        return
        
    print("\nAvailable cameras:")
    for index, resolution in cameras:
        print(f"Camera {index}: {resolution[0]}x{resolution[1]}")
    
    # Use the first available camera
    camera_index = cameras[0][0]
    cap = cv2.VideoCapture(camera_index)
    
    # Add camera check
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
        
    # Add camera properties check
    print(f"Camera resolution: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
    
    # Replace with your server URL
    server_url = 'http://52.38.44.83:8000/faces'
    detector = FaceDetector(server_url, throttle_seconds=10)
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to grab frame. Attempting to reconnect...")
            cap.release()
            cap = cv2.VideoCapture(camera_index)
            continue
            
        # Process frame and detect faces
        processed_frame, faces_data = detector.process_frame(frame)
        
        # Add status text with better visibility
        # White text with black outline for better readability
        def put_text(img, text, position, size=0.7):
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = 2
            # Black outline
            cv2.putText(img, text, position, font, size, (0, 0, 0), thickness + 1)
            # White text
            cv2.putText(img, text, position, font, size, (255, 255, 255), thickness)

        # Add status messages
        y_position = 30
        put_text(processed_frame, f"Faces detected: {len(faces_data)}", (10, y_position))
        
        # If faces detected, try to send to server
        if faces_data:
            if detector.should_send_request():
                success = detector.send_to_server(processed_frame, faces_data)
                if success:
                    put_text(processed_frame, "Sent to server!", (10, y_position + 30))
                else:
                    put_text(processed_frame, "Failed to send", (10, y_position + 30))
            else:
                # Show countdown timer
                time_diff = datetime.now() - detector.last_sent_time if detector.last_sent_time else None
                if time_diff:
                    seconds_left = max(0, detector.throttle_seconds - time_diff.total_seconds())
                    put_text(processed_frame, f'Next send in: {seconds_left:.1f}s', 
                           (10, y_position + 30))
        
        # Display the frame
        cv2.imshow('Face Detection', processed_frame)
        
        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()