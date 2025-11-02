import cv2
import mediapipe as mp
import numpy as np
import argparse

def calculate_angle(a, b, c):
    """
    Calculates the angle between three 3D points.
    'b' is the vertex of the angle.
    """
    a = np.array(a) # First point
    b = np.array(b) # Mid point (vertex)
    c = np.array(c) # End point
    
    # Calculate vectors
    ba = a - b
    bc = c - b
    
    # Calculate angle
    # The dot product formula: a.b = |a||b|cos(theta)
    # cos(theta) = (ba . bc) / (|ba| * |bc|)
    # theta = arccos( (ba . bc) / (|ba| * |bc|) )
    
    dot_product = np.dot(ba, bc)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    
    # Avoid division by zero
    if norm_ba == 0 or norm_bc == 0:
        return 0 # Or some default value, e.g., np.nan

    cosine_angle = dot_product / (norm_ba * norm_bc)
    
    # Clip values to avoid acos domain errors
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    angle_rad = np.arccos(cosine_angle)
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

def get_landmark_coords(landmarks, landmark_name):
    """
    Returns the [x, y, z] coordinates of a specific landmark.
    """
    lm = landmarks[mp.solutions.pose.PoseLandmark[landmark_name].value]
    return [lm.x, lm.y, lm.z]

def main(exercise_type, source):
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    # --- Exercise Specific Configuration ---
    if exercise_type == 'curl':
        # Landmarks to track for angle
        P1 = 'LEFT_SHOULDER'
        P2 = 'LEFT_ELBOW'
        P3 = 'LEFT_WRIST'
        
        # Landmarks for stability check (elbow shouldn't move)
        STABILITY_POINT = 'LEFT_ELBOW'
        ANCHOR_POINT = 'LEFT_SHOULDER' # Elbow position relative to shoulder
        
        # **FIX:** Widen state thresholds to be more forgiving than ROM thresholds
        # This helps detect imperfect reps.
        STATE_UP_THRESHOLD = 70    # Angle (degrees) to be considered "up"
        STATE_DOWN_THRESHOLD = 150 # Angle (degrees) to be considered "down"
        
        # Quality check thresholds (The "perfect" rep)
        ROM_MIN_THRESHOLD = 60     # Max flexion
        ROM_MAX_THRESHOLD = 160    # Max extension
        STABILITY_THRESHOLD = 0.1  # Max allowed movement (relative to shoulder-wrist distance)
        
    elif exercise_type == 'lateral_raise':
        # 
        # Landmarks to track for angle (Hip-Shoulder-Elbow)
        P1 = 'LEFT_HIP'
        P2 = 'LEFT_SHOULDER'
        P3 = 'LEFT_ELBOW' # We use the elbow to measure arm abduction
        
        # Landmarks for "straight arm" check
        ARM_P1 = 'LEFT_SHOULDER'
        ARM_P2 = 'LEFT_ELBOW'
        ARM_P3 = 'LEFT_WRIST'
        
        # **FIX:** State thresholds for logic: "up" is a LARGE angle, "down" is a SMALL angle
        STATE_UP_THRESHOLD = 75    # Angle (degrees) to be considered "up"
        STATE_DOWN_THRESHOLD = 30  # Angle (degrees) to be considered "down"
        
        # Quality check thresholds (The "perfect" rep)
        ROM_MIN_THRESHOLD = 80     # Peak abduction (HIGH angle)
        ROM_MAX_THRESHOLD = 20     # Full rest (LOW angle)
        ARM_STRAIGHT_THRESHOLD = 150 # Arm must be > 150 degrees
        
    else:
        print(f"Unknown exercise: {exercise_type}")
        return

    # --- MediaPipe and OpenCV Setup ---
    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)
    if not cap.isOpened():
        print(f"Error: Could not open video source '{source}'")
        return

    # --- Rep Counting and Scoring Variables ---
    rep_counter = 0
    current_stage = 'down' # Start in 'down' state
    
    good_reps = 0
    total_reps = 0
    feedback_message = ""
    
    # Variables for quality checks per rep
    current_rep_min_angle = 180
    current_rep_max_angle = 0
    stability_tracker = [] # Track movement of stability point

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video stream or error.")
                break
                
            # Recolor image to RGB for MediaPipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            
            # Make detection
            results = pose.process(image)
            
            # Recolor back to BGR for OpenCV
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            try:
                landmarks = results.pose_landmarks.landmark
                
                # --- 1. Get Coordinates ---
                p1_coords = get_landmark_coords(landmarks, P1)
                p2_coords = get_landmark_coords(landmarks, P2)
                p3_coords = get_landmark_coords(landmarks, P3)
                
                # --- 2. Calculate Main Angle ---
                angle = calculate_angle(p1_coords, p2_coords, p3_coords)
                
                # Update min/max angles for the current rep
                current_rep_min_angle = min(current_rep_min_angle, angle)
                current_rep_max_angle = max(current_rep_max_angle, angle)
                
                # --- 3. Stability Check (Example for Curl) ---
                if exercise_type == 'curl':
                    # Get elbow and shoulder coords
                    elbow_coords = np.array(get_landmark_coords(landmarks, STABILITY_POINT))
                    shoulder_coords = np.array(get_landmark_coords(landmarks, ANCHOR_POINT))
                    stability_tracker.append(elbow_coords)
                
                # --- 4. Rep Counting State Machine ---
                # **FIX:** This logic is now split by exercise type
                
                # --- CURL LOGIC ---
                if exercise_type == 'curl':
                    # State: UP (small angle)
                    if angle < STATE_UP_THRESHOLD:
                        current_stage = 'up'
                        
                    # State: DOWN (large angle) - Rep completed
                    if angle > STATE_DOWN_THRESHOLD and current_stage == 'up':
                        current_stage = 'down'
                        rep_counter += 1
                        total_reps += 1
                        
                        # --- 5. SCORE THE COMPLETED CURL REP ---
                        rep_is_good = True
                        feedback_message = ""
                        
                        # Check 1: ROM
                        if not (current_rep_min_angle < ROM_MIN_THRESHOLD and current_rep_max_angle > ROM_MAX_THRESHOLD):
                            rep_is_good = False
                            feedback_message = "Bad ROM!"
                        
                        # Check 2: Stability (This feedback is more important)
                        if len(stability_tracker) > 1:
                            movement = np.max(np.linalg.norm(np.diff(stability_tracker, axis=0), axis=1))
                            wrist_coords = np.array(get_landmark_coords(landmarks, P3))
                            arm_length = np.linalg.norm(shoulder_coords - wrist_coords)
                            
                            if arm_length > 0 and (movement / arm_length) > STABILITY_THRESHOLD:
                                rep_is_good = False
                                feedback_message = "Elbow moving!"

                        # Update score
                        if rep_is_good:
                            good_reps += 1
                            feedback_message = "Good Rep!"
                        
                        # Reset rep-specific trackers
                        current_rep_min_angle = 180
                        current_rep_max_angle = 0
                        stability_tracker = []

                # --- LATERAL RAISE LOGIC ---
                elif exercise_type == 'lateral_raise':
                    # State: UP (LARGE angle)
                    if angle > STATE_UP_THRESHOLD:
                        current_stage = 'up'
                    
                    # State: DOWN (SMALL angle) - Rep completed
                    if angle < STATE_DOWN_THRESHOLD and current_stage == 'up':
                        current_stage = 'down'
                        rep_counter += 1
                        total_reps += 1

                        # --- 5. SCORE THE COMPLETED LATERAL REP ---
                        rep_is_good = True
                        feedback_message = ""

                        # Check 1: ROM (**FIXED LOGIC**)
                        # Check if max angle > peak threshold AND min angle < rest threshold
                        if not (current_rep_max_angle > ROM_MIN_THRESHOLD and current_rep_min_angle < ROM_MAX_THRESHOLD):
                            rep_is_good = False
                            feedback_message = "Bad ROM!"
                        
                        # Check 2: Arm Straight (This feedback is more important)
                        arm_p1_coords = get_landmark_coords(landmarks, ARM_P1)
                        arm_p2_coords = get_landmark_coords(landmarks, ARM_P2)
                        arm_p3_coords = get_landmark_coords(landmarks, ARM_P3)
                        arm_angle = calculate_angle(arm_p1_coords, arm_p2_coords, arm_p3_coords)
                        
                        if arm_angle < ARM_STRAIGHT_THRESHOLD:
                            rep_is_good = False
                            feedback_message = "Keep arm straight!"

                        # Update score
                        if rep_is_good:
                            good_reps += 1
                            feedback_message = "Good Rep!"
                        
                        # Reset rep-specific trackers
                        current_rep_min_angle = 180
                        current_rep_max_angle = 0
                        # No stability_tracker to reset

            except Exception as e:
                # print(f"Error processing landmarks: {e}")
                pass # Fail silently if landmarks aren't visible
            
            # --- 6. CLI Output ---
            # Clear the terminal screen for a clean CLI feel
            print('\033[H\033[J', end='')  
            
            print("--- MEDIAPIPE EXERCISE CHECKER ---")
            print(f"EXERCISE: {exercise_type.upper()}")
            print(f"SOURCE: {source}")
            print("----------------------------------")
            print(f"REPS: {rep_counter}")
            print(f"STAGE: {current_stage}")
            print(f"SCORE: {good_reps} / {total_reps}")
            
            score_percent = (good_reps / total_reps) * 100 if total_reps > 0 else 0
            print(f"QUALITY: {score_percent:.2f}%")
            print(f"FEEDBACK: {feedback_message}")
            
            
            # --- 7. (Optional) Render Debug Window ---
            # Setup status box
            cv2.rectangle(image, (0, 0), (300, 150), (245, 117, 16), -1)
            
            # Rep data
            cv2.putText(image, 'REPS', (15, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, str(rep_counter), (10, 70), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Stage data
            cv2.putText(image, 'STAGE', (90, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, current_stage, (90, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Feedback
            cv2.putText(image, 'FEEDBACK', (15, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(image, feedback_message, (15, 120), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

            # Render detections
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), 
                                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2) 
                                     )               
            
            cv2.imshow('MediaPipe Pose', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("----------------------------------")
    print("Session Ended.")
    print(f"Final Score: {good_reps} / {total_reps} ({score_percent:.2f}%)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MediaPipe Exercise Quality Checker CLI')
    parser.add_argument('--exercise', type=str, required=True, 
                        help='Type of exercise to track (e.g., "curl", "lateral_raise")')
    parser.add_argument('--source', type=str, required=True, 
                        help='Video source (path to file or "0" for webcam)')
    
    args = parser.parse_args()
    main(args.exercise, args.source)