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


def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

@router.websocket("/ws/analyze")
async def analyze_pose(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")

    init_msg = await websocket.receive_text()
    try:
        config = json.loads(init_msg)
        exercise = config.get("exercise")
    except Exception:
        await websocket.send_text("ERROR: Invalid init message.")
        await websocket.close()
        return

    print(f"\n\nAnalyzing exercise: {exercise}\n\n")
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    form_history = []
    start_time = time.time()

    try:
        while True:
            # Check 30-second timeout
            if time.time() - start_time >= 10:
                break

            # Receive bytes from frontend
            frame_bytes = await websocket.receive_bytes()

            # Decode frame
            np_arr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)

            is_correct = 0

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                try:
                    # Example: LEFT_ELBOW analysis
                    points = [
                        [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                        [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
                        [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                    ]
                    angle = calculate_angle(*points)
                    if angle < 30 or angle > 160:
                        is_correct = 1

                    # Annotate frame
                    h, w = frame.shape[:2]
                    elbow_coords = points[1]
                    cv2.putText(frame, f"{int(angle)} deg",
                                (int(elbow_coords[0]*w), int(elbow_coords[1]*h - 20)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                except Exception as e:
                    print("Pose error:", e)

                # Draw pose
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            form_history.append(is_correct)

            # Encode and send back the annotated frame
            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send_bytes(buffer.tobytes())

    except WebSocketDisconnect:
        print("Client disconnected")

    # After 30 seconds: Send final score
    score = (sum(form_history) / len(form_history)) * 100 if form_history else 0
    print(f"Sending final score: {score}")
    await websocket.send_text(f"SCORE:{score:.2f}")

    await websocket.close()
