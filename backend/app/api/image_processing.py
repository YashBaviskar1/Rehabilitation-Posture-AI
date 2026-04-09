from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app import schemas, models
from app.db import get_db
from app.api.utils import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import cv2
from datetime import datetime
import numpy as np
import base64, json
from PIL import Image
from io import BytesIO
from ultralytics import YOLO

router = APIRouter(prefix="/analyse")



def base64_to_image(base64_str: str) -> np.ndarray:
    """Convert base64 string to OpenCV image (numpy array)."""
    header, encoded = base64_str.split(",", 1)
    img_data = base64.b64decode(encoded)
    pil_image = Image.open(BytesIO(img_data)).convert("RGB")
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def image_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image to base64 string."""
    _, buffer = cv2.imencode('.jpg', image)
    encoded = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"



@router.post("/test")
async def analyse_image(request: Request):
    data = await request.json()
    base64_image = data.get("image")

    if not base64_image:
        return {"error": "No image received"}

    # Decode the image
    image = base64_to_image(base64_image)

    # --- Basic Processing: Edge Detection ---
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Convert back to base64 and return
    edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)  # to keep 3 channels
    result_base64 = image_to_base64(edges_color)

    return {
        "processed_image": result_base64,
        "message": "Edge detection completed"
    }



@router.websocket("/ws/test")
async def image_analysis_websocket(websocket: WebSocket):
    await websocket.accept()
    # Step 1: Receive the image blob as bytes
    image_bytes = await websocket.receive_bytes()
    
    # Step 2: Convert bytes to NumPy array
    nparr = np.frombuffer(image_bytes, np.uint8)

    # Step 3: Decode into image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        print("Failed to decode image")
        return
    
    # Step 4: Save the image
    save_path = f"images/{datetime.now().timestamp()}.jpg"
    cv2.imwrite(save_path, img)
    
    print(f"Image saved to {save_path}")
    try:
        while True:
                message = await websocket.receive_bytes()
                # print("Received binary data of length:", len(message))
                frame_bytes = message
                # Decode bytes to image
                nparr = np.frombuffer(frame_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Process - edge detection (Canny)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 100, 200)
                # Convert single channel back to 3-channel for JPG encoding
                edges_color = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                
                # Encode processed image to bytes
                _, buffer = cv2.imencode('.jpg', edges_color)
                processed_bytes = buffer.tobytes()
                
                # Send processed image bytes back to client
                await websocket.send_bytes(processed_bytes)
                                
    except WebSocketDisconnect:
        print(f"\n\nDisconnected\n\n")





# Load YOLOv8 model on GPU (device=0)
model = YOLO('yolov8n.pt')  # Use yolov8s.pt, yolov8m.pt, or custom weights for different accuracy/speed
model.to('cuda')

@router.websocket("/ws/yolo")
async def image_object_detection(websocket: WebSocket):
    await websocket.accept()
    # Step 1: Receive the image blob as bytes
    image_bytes = await websocket.receive_bytes()
    
    # Step 2: Convert bytes to NumPy array
    nparr = np.frombuffer(image_bytes, np.uint8)

    # Step 3: Decode into image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        print("Failed to decode image")
        return
    
    # Step 4: Save the image
    save_path = f"images/{datetime.now().timestamp()}.jpg"
    cv2.imwrite(save_path, img)
    
    # print(f"Image saved to {save_path}")
    try:
        while True:
            frame_bytes = await websocket.receive_bytes()
            img = cv2.imdecode(np.frombuffer(frame_bytes, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue

            # YOLOv8 expects RGB, so convert
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = model(img_rgb)

            # Draw bounding boxes and labels using OpenCV
            if len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = f"{model.names[cls]} {conf:.2f}"

                    if conf < 0.3:
                        color_tuple = (0,0,255)
                    elif conf > 0.75:
                        color_tuple = (0,255,0)
                    else:
                        color_tuple = (255,0,0)

                    # Draw rectangle and label (convert to BGR for OpenCV)
                    cv2.rectangle(img, (x1, y1), (x2, y2), color_tuple, 2)
                    cv2.putText(img, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_tuple, 2)

            # Encode and send processed image
            _, processed_bytes = cv2.imencode('.jpg', img)
            await websocket.send_bytes(processed_bytes.tobytes())
    except Exception as e:
        print("WebSocket error or client disconnect:", e)