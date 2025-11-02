import cv2
import websockets
import asyncio
import json
import time
import numpy as np

# --- Configuration ---
WEBSOCKET_URI = "ws://127.0.0.1:8000/pose/ws/analyze"
VIDEO_SOURCE = 0  # Use 0 for your webcam
# VIDEO_SOURCE = "path/to/test_video.mp4" # Or use a video file
EXERCISE_TO_TEST = "curl"  # Change to "lateral_raise" to test the other
# ---------------------

async def send_frames(websocket, video_source, exercise_id):
    """
    Connects, sends init config, and then streams video frames.
    """
    try:
        # 1. Send init message
        config = {
            "exercise_id": exercise_id,
            "patient_id": "test_patient_001",
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(config))
        print(f"Client: Sent init config for {exercise_id}")

        # 2. Open video source and send frames
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"Error: Could not open video source '{video_source}'")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Client: Video source finished.")
                break
            
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            
            try:
                await websocket.send(buffer.tobytes())
            except websockets.exceptions.ConnectionClosed:
                print("Client: Send failed, connection closed.")
                break
            
            # Slow down to ~30fps, also allows other async tasks to run
            await asyncio.sleep(0.03) 
            
    except Exception as e:
        print(f"Client Send Error: {e}")
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()
        print("Client: Send task finished.")


async def receive_frames(websocket):
    """
    Receives messages from the server and displays them.
    Handles both image bytes and the final score string.
    """
    try:
        while True:
            response = await websocket.recv()
            
            if isinstance(response, str):
                # This is the final JSON score
                print("\n--- CLIENT: FINAL SCORE RECEIVED ---")
                print(json.dumps(json.loads(response), indent=2))
                print("--------------------------------------")
                break # Got the final score, we're done.
            
            else:
                # This is image bytes
                np_arr = np.frombuffer(response, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    cv2.imshow('Test Client - Receiving', img)
                    # Press 'q' to quit the client
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Client: User pressed 'q', stopping.")
                        break
                
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client Receive: Connection closed (Code: {e.code})")
    except Exception as e:
        print(f"Client Receive Error: {e}")
    finally:
        cv2.destroyAllWindows()
        print("Client: Receive task finished.")


async def main_test():
    """
    Connects to the websocket and runs send/receive tasks.
    """
    print(f"Connecting to {WEBSOCKET_URI}...")
    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            print("Client: Connected!")
            
            # Create and run send and receive tasks concurrently
            send_task = asyncio.create_task(send_frames(websocket, VIDEO_SOURCE, EXERCISE_TO_TEST))
            receive_task = asyncio.create_task(receive_frames(websocket))
            
            # Wait for either task to finish
            done, pending = await asyncio.wait(
                [send_task, receive_task], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Clean up: cancel any pending tasks
            for task in pending:
                task.cancel()
                
    except Exception as e:
        print(f"Client: Failed to connect or run. Is the server running? \nError: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main_test())
    except KeyboardInterrupt:
        print("Client: Interrupted by user.")