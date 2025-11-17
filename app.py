from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO
import cv2
import time

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
camera = cv2.VideoCapture(0)
model = YOLO('yolov8n.pt')

# Global variable to store detection count
detection_count = 0
detected_classes = {}

frame_count = 0
skip_frames = 2

def generate_frames():
    global frame_count, detection_count, detected_classes
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
            last_annotated_frame = results[0].plot()
            
            # Count detected objects
            detection_count = len(results[0].boxes)
            
            # Count by class (optional)
            detected_classes = {}
            for box in results[0].boxes:
                class_id = int(box.cls[0])
                class_name = results[0].names[class_id]
                detected_classes[class_name] = detected_classes.get(class_name, 0) + 1
                
        elif last_annotated_frame is not None:
            last_annotated_frame = last_annotated_frame
            
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
        'classes': detected_classes
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)