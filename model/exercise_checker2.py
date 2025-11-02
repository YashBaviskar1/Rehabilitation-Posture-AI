import cv2
import mediapipe as mp
import numpy as np
import argparse
import time

# ---------- ANGLE CALCULATION ----------
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    ba = a - b
    bc = c - b

    dot_product = np.dot(ba, bc)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba == 0 or norm_bc == 0:
        return 0

    cosine_angle = dot_product / (norm_ba * norm_bc)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))

    return angle

# ---------- LANDMARK GETTER ----------
def get_landmark_coords(landmarks, landmark_name):
    lm = landmarks[mp.solutions.pose.PoseLandmark[landmark_name].value]
    return [lm.x, lm.y, lm.z]

# ---------- MAIN ----------
def main(exercise_type, source):
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(int(source) if source.isdigit() else source)

    if not cap.isOpened():
        print(f"Error: Could not open video source '{source}'")
        return

    # --- Exercise-specific setup ---
    if exercise_type == "curl":
        P1, P2, P3 = "LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"
        STATE_UP_THRESHOLD, STATE_DOWN_THRESHOLD = 70, 150
        ROM_MIN, ROM_MAX = 60, 160
        STABILITY_THRESHOLD = 0.12

    elif exercise_type == "lateral_raise":
        P1, P2, P3 = "LEFT_HIP", "LEFT_SHOULDER", "LEFT_ELBOW"
        ARM_P1, ARM_P2, ARM_P3 = "LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"
        STATE_UP_THRESHOLD, STATE_DOWN_THRESHOLD = 75, 30
        ROM_MIN, ROM_MAX = 80, 20
        ARM_STRAIGHT_THRESHOLD = 150

    elif exercise_type == "neck_turn":
        # Simple head rotation detection using nose and shoulders
        P_NOSE = mp_pose.PoseLandmark.NOSE
        P_LSHOULDER = mp_pose.PoseLandmark.LEFT_SHOULDER
        P_RSHOULDER = mp_pose.PoseLandmark.RIGHT_SHOULDER
        TURN_THRESHOLD = 0.05  # relative nose x position
    elif exercise_type == "squat":
        P1, P2, P3 = "LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"
        STATE_UP_THRESHOLD, STATE_DOWN_THRESHOLD = 160, 90
        ROM_MIN, ROM_MAX = 80, 160
    else:
        print(f"Unknown exercise: {exercise_type}")
        return

    # --- Variables ---
    rep_counter, good_reps, total_reps = 0, 0, 0
    current_stage = "down"
    feedback = ""
    current_rep_min, current_rep_max = 180, 0
    rep_start_time = None
    rep_durations = []

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of stream.")
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                # ---------- CURL ----------
                if exercise_type == "curl":
                    p1, p2, p3 = get_landmark_coords(landmarks, P1), get_landmark_coords(landmarks, P2), get_landmark_coords(landmarks, P3)
                    angle = calculate_angle(p1, p2, p3)
                    current_rep_min, current_rep_max = min(current_rep_min, angle), max(current_rep_max, angle)

                    # Up phase
                    if angle < STATE_UP_THRESHOLD and current_stage == "down":
                        current_stage = "up"
                        rep_start_time = time.time()

                    # Down phase
                    elif angle > STATE_DOWN_THRESHOLD and current_stage == "up":
                        current_stage = "down"
                        rep_counter += 1
                        total_reps += 1
                        rep_time = time.time() - rep_start_time if rep_start_time else 0
                        rep_durations.append(rep_time)

                        rep_is_good = current_rep_min < ROM_MIN and current_rep_max > ROM_MAX
                        feedback = "Good Rep!" if rep_is_good else "Bad ROM!"
                        if rep_is_good:
                            good_reps += 1
                        current_rep_min, current_rep_max = 180, 0

                # ---------- LATERAL RAISE ----------
                elif exercise_type == "lateral_raise":
                    p1, p2, p3 = get_landmark_coords(landmarks, P1), get_landmark_coords(landmarks, P2), get_landmark_coords(landmarks, P3)
                    angle = calculate_angle(p1, p2, p3)
                    current_rep_min, current_rep_max = min(current_rep_min, angle), max(current_rep_max, angle)

                    if angle > STATE_UP_THRESHOLD and current_stage == "down":
                        current_stage = "up"
                        rep_start_time = time.time()

                    elif angle < STATE_DOWN_THRESHOLD and current_stage == "up":
                        current_stage = "down"
                        rep_counter += 1
                        total_reps += 1
                        rep_time = time.time() - rep_start_time if rep_start_time else 0
                        rep_durations.append(rep_time)

                        arm_p1 = get_landmark_coords(landmarks, ARM_P1)
                        arm_p2 = get_landmark_coords(landmarks, ARM_P2)
                        arm_p3 = get_landmark_coords(landmarks, ARM_P3)
                        arm_angle = calculate_angle(arm_p1, arm_p2, arm_p3)

                        rep_is_good = (
                            current_rep_max > ROM_MIN
                            and current_rep_min < ROM_MAX
                            and arm_angle > ARM_STRAIGHT_THRESHOLD
                        )

                        # Scoring based on ROM + Speed
                        rom_score = min(100, (current_rep_max - current_rep_min))
                        speed_score = max(0, 100 - (rep_time * 10))
                        total_score = 0.6 * rom_score + 0.4 * speed_score

                        if rep_is_good:
                            feedback = f"Good Rep! Score: {total_score:.1f}"
                            good_reps += 1
                        else:
                            feedback = "Keep Arm Straight / Full ROM!"

                        current_rep_min, current_rep_max = 180, 0

                # ---------- NECK TURN ----------
                elif exercise_type == "neck_turn":
                    nose = landmarks[P_NOSE]
                    left_shoulder = landmarks[P_LSHOULDER]
                    right_shoulder = landmarks[P_RSHOULDER]

                    center = (left_shoulder.x + right_shoulder.x) / 2
                    deviation = nose.x - center

                    if deviation > TURN_THRESHOLD and current_stage == "center":
                        current_stage = "right"
                        rep_start_time = time.time()
                    elif deviation < -TURN_THRESHOLD and current_stage == "center":
                        current_stage = "left"
                        rep_start_time = time.time()
                    elif abs(deviation) < 0.01 and current_stage in ["left", "right"]:
                        rep_counter += 1
                        total_reps += 1
                        rep_time = time.time() - rep_start_time if rep_start_time else 0
                        rep_durations.append(rep_time)
                        good_reps += 1
                        feedback = "Good Neck Turn!"
                        current_stage = "center"

                # ---------- SQUAT ----------
                elif exercise_type == "squat":
                    p1, p2, p3 = get_landmark_coords(landmarks, P1), get_landmark_coords(landmarks, P2), get_landmark_coords(landmarks, P3)
                    angle = calculate_angle(p1, p2, p3)
                    current_rep_min, current_rep_max = min(current_rep_min, angle), max(current_rep_max, angle)

                    if angle < STATE_DOWN_THRESHOLD and current_stage == "up":
                        current_stage = "down"
                        rep_start_time = time.time()
                    elif angle > STATE_UP_THRESHOLD and current_stage == "down":
                        current_stage = "up"
                        rep_counter += 1
                        total_reps += 1
                        rep_time = time.time() - rep_start_time if rep_start_time else 0
                        rep_durations.append(rep_time)
                        rep_is_good = current_rep_min < ROM_MIN and current_rep_max > ROM_MAX
                        feedback = "Good Squat!" if rep_is_good else "Incomplete!"
                        if rep_is_good:
                            good_reps += 1
                        current_rep_min, current_rep_max = 180, 0

            except Exception:
                pass

            # ---------- DISPLAY ----------
            cv2.rectangle(image, (0, 0), (320, 150), (245, 117, 16), -1)
            cv2.putText(image, f"REPS: {rep_counter}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(image, f"STAGE: {current_stage}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(image, f"{feedback}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow("Exercise Tracker", image)
            if cv2.waitKey(10) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("----------------------------------")
    print(f"Final Reps: {rep_counter} | Good Reps: {good_reps}")
    print(f"Avg Rep Time: {np.mean(rep_durations):.2f}s" if rep_durations else "")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MediaPipe Exercise Quality Tracker")
    parser.add_argument("--exercise", type=str, required=True,
                        help='Type: "curl", "lateral_raise", "neck_turn", "squat"')
    parser.add_argument("--source", type=str, required=True,
                        help='Video path or "0" for webcam')
    args = parser.parse_args()
    main(args.exercise, args.source)
