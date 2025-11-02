from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from app import models, schemas, db
from app.api import authentication, users, exercises, image_processing, scores, pose_net
import uvicorn
import os
load_dotenv()


# FastAPI app
app = FastAPI()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Create the database tables
models.Base.metadata.create_all(bind=db.engine)

# Allow all origins (not safe for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

def middleware():
# Custom Middleware Example
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     print(f"Incoming request {request.method} {request.url}")
#     response = await call_next(request)
#     print(f"Response status: {response.status_code}")
#     return response
    return





# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     user = fake_users_db.get(username)
#     if user is None:
#         raise credentials_exception
#     return User(username=username)


app.include_router(prefix="/api", router=authentication.router)

app.include_router(prefix="/api", router=users.router)

app.include_router(prefix="/api", router=exercises.router)

app.include_router(prefix="/api", router=image_processing.router)

app.include_router(prefix="/api", router=scores.router)

app.include_router(prefix="/api", router=pose_net.router)

@app.get("/health")
async def health():
    return {"status": "Healthy!"}


# Path to the built React app
REACT_DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")
ASSETS_DIR = os.path.join(REACT_DIST_DIR, "assets")

# Mount the React build folder
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

@app.get("/")
async def serve_root():
    return FileResponse(os.path.join(REACT_DIST_DIR, "index.html"))

@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    return FileResponse(os.path.join(REACT_DIST_DIR, "index.html"))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)