import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

def moving_average(data, window_size):
    if len(data) < window_size:
        return data
    return np.convolve(data, np.ones(window_size), 'valid') / window_size

def analyze_video_form(video_path, joint='LEFT_ELBOW', angle_threshold=(30, 160), window_size=50):
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video stream: {video_path}")

    form_history = []
    print("Press 'q' to quit.")
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Stream ended or frame grab failed.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        is_correct = 0

        if results.pose_landmarks:
            try:
                landmarks = results.pose_landmarks.landmark
                if joint == 'LEFT_ELBOW':
                    points = [
                        [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                        [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
                        [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    ]
                else:
                    points = [
                        [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
                        [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y],
                        [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    ]

                angle = calculate_angle(*points)

                # Draw angle on frame
                elbow_coords = points[1]
                h, w = frame.shape[:2]
                cv2.putText(frame, f"{int(angle)} deg", 
                            (int(elbow_coords[0] * w), int(elbow_coords[1] * h - 20)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                if angle < angle_threshold[0] or angle > angle_threshold[1]:
                    is_correct = 1

            except Exception as e:
                print("Angle calc error:", e)
                is_correct = 0

        form_history.append(is_correct)

        # Draw pose landmarks
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2)
        )

        # Show video
        cv2.imshow("Pose Analysis", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    moving_avg = moving_average(form_history, window_size)
    overall_correctness = (sum(form_history) / len(form_history)) * 100 if form_history else 0.0

    return {
        'form_history': form_history,
        'moving_avg': moving_avg.tolist() if isinstance(moving_avg, np.ndarray) else moving_avg,
        'overall_correctness': overall_correctness
    }

# Run the analysis on DroidCam stream
video_path = "http://192.168.0.101:4747/video"
result = analyze_video_form(video_path)
print("Analysis Result:", result)
