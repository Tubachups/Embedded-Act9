from flask import Flask, render_template, Response, jsonify
from gpiozero import DigitalInputDevice, Buzzer
from ultralytics import YOLO
import cv2
import time

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
camera = cv2.VideoCapture(0)
model = YOLO('yolov8n.pt')
motion_sensor = DigitalInputDevice(16)
buzzer = Buzzer(21)

# Global variable to store detection count
detection_count = 0
detected_classes = {}

frame_count = 0
skip_frames = 2

FOREIGN_OBJECT_CLASSES = {'bottle', 'cup', 'knife', 'backpack', 'handbag', 'scissors'}

def map_class_name(class_name):
    """Map specific classes to 'Foreign Object'"""
    if class_name.lower() in FOREIGN_OBJECT_CLASSES:
        return "Foreign Object"
    return class_name


def generate_frames():
    global frame_count, detection_count, detected_classes, foreign_object_detected
    last_annotated_frame = None
    
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        frame_count += 1
        
        current_time = time.time()
        
        # Only run detection on some frames
        if frame_count % skip_frames == 0:
            # Configure imgsz for fps or accuracy
            results = model(frame, conf=0.5, verbose=False, imgsz=160)
            
            # Don't use plot() - start with original frame
            last_annotated_frame = frame.copy()
            
            # Count detected objects
            detection_count = len(results[0].boxes)
            
            # Reset foreign object flag
            foreign_object_detected = False
            
            # Count by class (optional)
            detected_classes = {}
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                original_name = results[0].names[class_id]
                display_name = map_class_name(original_name)
                detected_classes[display_name] = detected_classes.get(display_name, 0) + 1
                
                # Check if foreign object detected
                if display_name == "Foreign Object":
                    foreign_object_detected = True
                
                # Draw custom bounding box with mapped name
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                
                # Color: Red for foreign objects, Green for others
                color = (0, 0, 255) if display_name == "Foreign Object" else (0, 255, 0)
                
                cv2.rectangle(last_annotated_frame, (x1, y1), (x2, y2), color, 2)
                label = f"{display_name}: {conf:.2f}"
                cv2.putText(last_annotated_frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Control buzzer based on foreign object detection
            if foreign_object_detected:
                buzzer.on()
            else:
                buzzer.off()
                
        elif last_annotated_frame is None:
            last_annotated_frame = frame.copy()
            
        if last_annotated_frame is not None:
            # Add detection count to frame
            cv2.putText(last_annotated_frame, f'Objects: {detection_count}', 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', last_annotated_frame, 
                                      [cv2.IMWRITE_JPEG_QUALITY, 70])
            frame = buffer.tobytes()
            
            yield(b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
            
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_stats')
def detection_stats():
    """API endpoint to get detection statistics"""
    return jsonify({
        'total': detection_count,
        'classes': detected_classes,
        'motion_detected': motion_sensor.is_active
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)