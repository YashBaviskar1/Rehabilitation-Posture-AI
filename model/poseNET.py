import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """Calculate the angle between three points in degrees."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def moving_average(data, window_size):
    """Compute moving average over a list of values."""
    if not data:
        return []
    return np.convolve(data, np.ones(window_size), 'valid') / window_size

def analyze_video_form(video_path, joint='LEFT_ELBOW', angle_threshold=(30, 160), window_size=50):
    """
    Analyze video frames for joint form correctness.

    Args:
        video_path (str): Path to the input video file.
        joint (str): Joint to analyze ('LEFT_ELBOW' or 'RIGHT_ELBOW').
        angle_threshold (tuple): Min and max angle to consider form correct.
        window_size (int): Window size for moving average smoothing.

    Returns:
        dict: {
            'form_history': list of 0/1 correctness per frame,
            'moving_avg': smoothed correctness values,
            'overall_correctness': percentage
        }
    """
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video file: {video_path}")
    
    form_history = []
    frame_count = 200
    while cap.isOpened():
        success, frame = cap.read()
        print(frame_count)
        frame_count -= 1
        if not frame_count:
            break
        if not success:
            break
        
        # Convert BGR to RGB and process pose
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(frame_rgb)
        is_correct = 0
        
        if pose_results.pose_landmarks:
            try:
                landmarks = pose_results.pose_landmarks.landmark
                
                if joint == 'LEFT_ELBOW':
                    points = [
                        [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                        [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
                        [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    ]
                else:  # RIGHT_ELBOW
                    points = [
                        [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
                        [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y],
                        [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    ]
                
                angle = calculate_angle(*points)
                if angle < angle_threshold[0] or angle > angle_threshold[1]:
                    is_correct = 1
                
            except:
                is_correct = 0
        
        form_history.append(is_correct)

        cv2.imshow("POSE DETECTION", frame_rgb)
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Compute moving average for smoother visualization
    moving_avg = moving_average(form_history, window_size) if len(form_history) > window_size else form_history
    
    # Overall correctness percentage
    overall_correctness = (sum(form_history) / len(form_history)) * 100 if form_history else 0.0
    
    return {
        'form_history': form_history,
        'moving_avg': moving_avg,
        'overall_correctness': overall_correctness
    }

vedio_path = "http://192.168.0.101:4747/video"

result = analyze_video_form(vedio_path)
print(result)
