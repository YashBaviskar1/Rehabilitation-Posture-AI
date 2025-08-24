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

