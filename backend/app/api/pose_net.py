from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import cv2
import numpy as np
import mediapipe as mp
import time
import asyncio
import json

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

router = APIRouter(prefix="/pose")


# def calculate_angle(a, b, c):
#     a, b, c = np.array(a), np.array(b), np.array(c)
#     radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
#     angle = np.abs(radians * 180.0 / np.pi)
#     return 360 - angle if angle > 180 else angle

# @router.websocket("/ws/analyze")
# async def analyze_pose(websocket: WebSocket):
#     await websocket.accept()
#     print("WebSocket connected")

#     init_msg = await websocket.receive_text()
#     try:
#         config = json.loads(init_msg)
#         exercise_id = config.get("exercise_id")
#         patient_id = config.get("patient_id")
#         timestamp = config.get("timestamp")
#     except Exception:
#         await websocket.send_text("ERROR: Invalid init message.")
#         await websocket.close()
#         return

#     print(f"\n\nAnalyzing exercise: {exercise_id} for patient {patient_id} on {timestamp}\n\n")
#     pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#     form_history = []
#     start_time = time.time()

#     try:
#         while True:
#             # Check 30-second timeout
#             if time.time() - start_time >= 15:
#                 break

#             # Receive bytes from frontend
#             frame_bytes = await websocket.receive_bytes()

#             # Decode frame
#             np_arr = np.frombuffer(frame_bytes, np.uint8)
#             frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             results = pose.process(frame_rgb)

#             is_correct = 0

#             if results.pose_landmarks:
#                 landmarks = results.pose_landmarks.landmark
#                 try:
#                     # Example: LEFT_ELBOW analysis
#                     points = [
#                         [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
#                          landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
#                         [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
#                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
#                         [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
#                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
#                     ]
#                     angle = calculate_angle(*points)
#                     if angle < 30 or angle > 160:
#                         is_correct = 1

#                     # Annotate frame
#                     h, w = frame.shape[:2]
#                     elbow_coords = points[1]
#                     cv2.putText(frame, f"{int(angle)} deg",
#                                 (int(elbow_coords[0]*w), int(elbow_coords[1]*h - 20)),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#                 except Exception as e:
#                     print("Pose error:", e)

#                 # Draw pose
#                 mp_drawing.draw_landmarks(
#                     frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

#             form_history.append(is_correct)

#             # Encode and send back the annotated frame
#             _, buffer = cv2.imencode('.jpg', frame)
#             await websocket.send_bytes(buffer.tobytes())

#     except WebSocketDisconnect:
#         print("Client disconnected")

#     # After 30 seconds: Send final score
#     score = (sum(form_history) / len(form_history)) * 100 if form_history else 0
#     print(f"Sending final score: {score}")
#     await websocket.send_text(f"SCORE:{score:.2f}")

#     await websocket.close()



# --- Helper Functions (Using the 3D versions from your standalone script) ---

def calculate_angle(a, b, c):
    """
    Calculates the angle between three 3D points.
    'b' is the vertex of the angle.
    """
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

def get_landmark_coords(landmarks, landmark_name):
    """
    Returns the [x, y, z] coordinates of a specific landmark.
    """
    lm = landmarks[mp.solutions.pose.PoseLandmark[landmark_name].value]
    return [lm.x, lm.y, lm.z]

EXERCISES = {1: "curl", 2: "lateral_raise"}

# --- WebSocket Endpoint (Your integrated code) ---

@router.websocket("/ws/analyze")
async def analyze_pose(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")

    # --- 1. Receive Initialization Message ---
    init_msg = await websocket.receive_text()
    try:
        config = json.loads(init_msg)
        exercise_id = config.get("exercise_id")
        patient_id = config.get("patient_id")
        timestamp = config.get("timestamp")
        if EXERCISES[exercise_id] not in ["curl", "lateral_raise"]:
            raise ValueError(f"Unknown exercise_id: {exercise_id}")
    except Exception as e:
        print(f"Error: Invalid init message. {e}")
        await websocket.send_text(f"ERROR: Invalid init message. {e}")
        await websocket.close()
        return

    print(f"\nAnalyzing exercise: {EXERCISES[exercise_id]} for patient {patient_id} on {timestamp}\n")
    
    # --- 2. Initialize Pose Model and State Variables ---
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    start_time = time.time()
    # Using the 30-second timeout from your example
    SESSION_TIMEOUT = 15  

    # --- Exercise-specific setup ---
    if EXERCISES[exercise_id] == "curl":
        P1, P2, P3 = "LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"
        STATE_UP_THRESHOLD, STATE_DOWN_THRESHOLD = 70, 150
        ROM_MIN, ROM_MAX = 60, 160
    
    elif EXERCISES[exercise_id] == "lateral_raise":
        P1, P2, P3 = "LEFT_HIP", "LEFT_SHOULDER", "LEFT_ELBOW"
        ARM_P1, ARM_P2, ARM_P3 = "LEFT_SHOULDER", "LEFT_ELBOW", "LEFT_WRIST"
        STATE_UP_THRESHOLD, STATE_DOWN_THRESHOLD = 75, 30
        ROM_MIN, ROM_MAX = 70, 20
        ARM_STRAIGHT_THRESHOLD = 120

    print(f"\n\nExercise assigned {P1}\n\n")

    # --- State Variables ---
    rep_counter, good_reps, total_reps = 0, 0, 0
    current_stage = "down"
    feedback = ""
    current_rep_min, current_rep_max = 180, 0
    rep_start_time = None
    rep_durations = []
    
    final_data_sent = False

    try:
        while True:
            # --- 3. Check Timeout ---
            if time.time() - start_time >= SESSION_TIMEOUT:
                print("Session timeout.")
                break

            # --- 4. Receive and Decode Frame ---
            frame_bytes = await websocket.receive_bytes()
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            results = pose.process(frame_rgb)
            frame_rgb.flags.writeable = True
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR) # Re-assign to annotated frame

            # --- 5. Rep Counting Logic ---
            try:
                landmarks = results.pose_landmarks.landmark

                # ---------- CURL ----------
                if EXERCISES[exercise_id] == "curl":
                    p1 = get_landmark_coords(landmarks, P1)
                    p2 = get_landmark_coords(landmarks, P2)
                    p3 = get_landmark_coords(landmarks, P3)
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
                        feedback = "Good Rep!" if rep_is_good else "Bad Rep!"
                        if rep_is_good:
                            good_reps += 1
                        current_rep_min, current_rep_max = 180, 0

                # ---------- LATERAL RAISE ----------
                elif EXERCISES[exercise_id] == "lateral_raise":
                    p1 = get_landmark_coords(landmarks, P1)
                    p2 = get_landmark_coords(landmarks, P2)
                    p3 = get_landmark_coords(landmarks, P3)
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
                        print(f"\n\n{ arm_angle > ARM_STRAIGHT_THRESHOLD} \n {current_rep_min < ROM_MAX} \n {current_rep_max > ROM_MIN}")
                        
                        if rep_is_good:
                            feedback = "Good Rep!"
                            good_reps += 1
                        else:
                            feedback = "Keep Arm Straight / Full ROM!"

                        current_rep_min, current_rep_max = 180, 0

            except Exception:
                pass # Fail silently if landmarks aren't visible

            # --- 6. Annotate and Send Frame ---
            cv2.rectangle(frame, (0, 0), (320, 150), (245, 117, 16), -1)
            cv2.putText(frame, f"REPS: {rep_counter}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"STAGE: {current_stage}", (10, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f"{feedback}", (10, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                )

            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send_bytes(buffer.tobytes())

    except WebSocketDisconnect:
        print("Client disconnected")
    
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # --- 7. Send Final Score and Close ---
        if not final_data_sent:
            avg_time = np.mean(rep_durations) if rep_durations else 0
            final_data = {
                "status": "session_ended",
                "total_reps": total_reps,
                "good_reps": good_reps,
                "average_rep_time": f"{avg_time:.2f}s",
                "exercise_id": exercise_id,
                "patient_id": patient_id
            }

            final_data = (good_reps/total_reps)*100 if total_reps else 0
            try:
                # await websocket.send_text(json.dumps(final_data))
                await websocket.send_text(f"SCORE: {final_data:.2f}")
                print(f"Sent final data: {final_data}")
            except Exception as e:
                print(f"Could not send final data: {e}")
        
        pose.close()
        await websocket.close()
        print("WebSocket connection closed")