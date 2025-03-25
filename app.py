from flask import Flask, Response, render_template
import cv2
import mediapipe as mp
import numpy as np
import os

app = Flask(__name__)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

detected_poses = []

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

def detect_pose(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    return results.pose_landmarks

def classify_pose(landmarks):
    if landmarks is None:
        return "Unknown"
    
    try:
        left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_elbow = landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_elbow = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
        left_wrist = landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        
        left_elbow_angle = calculate_angle(
            [left_shoulder.x, left_shoulder.y], 
            [left_elbow.x, left_elbow.y], 
            [left_wrist.x, left_wrist.y]
        )
        
        right_elbow_angle = calculate_angle(
            [right_shoulder.x, right_shoulder.y], 
            [right_elbow.x, right_elbow.y], 
            [right_wrist.x, right_wrist.y]
        )
        
        if 160 < left_elbow_angle < 180 and 160 < right_elbow_angle < 180:
            return "T-Pose"
        elif 80 < left_elbow_angle < 100:
            return "Right Angle Pose"
        elif left_wrist.y < left_shoulder.y and right_wrist.y < right_shoulder.y:
            return "Raised Arms Pose"
        else:
            return "Unknown Pose"
    
    except Exception as e:
        return f"Error: {e}"

def save_detected_poses():
    with open("detected_poses.txt", "w") as f:
        for pose in detected_poses:
            f.write(pose + "\n")

def save_pose_image(frame, pose_label, landmarks):
    if not os.path.exists("static/captured_poses"):
        os.makedirs("static/captured_poses")
    
    mp_drawing.draw_landmarks(frame, landmarks, mp_pose.POSE_CONNECTIONS)
    image_path = f"static/captured_poses/{pose_label}_{len(detected_poses)}.jpg"
    # print(image_path)
    cv2.imwrite(image_path, frame)

def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            landmarks = detect_pose(frame)
            pose_label = classify_pose(landmarks)
            detected_poses.append(pose_label)
            save_pose_image(frame, pose_label, landmarks)
            mp_drawing.draw_landmarks(frame, landmarks, mp_pose.POSE_CONNECTIONS)
            cv2.putText(frame, pose_label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()
    save_detected_poses()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()

# Create necessary folders
if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("templates"):
    os.makedirs("templates")