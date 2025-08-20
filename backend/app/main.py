from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from app import models, schemas, db
from app.api import authentication, users, exercises
import os
load_dotenv()


# FastAPI app
app = FastAPI()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Create the database tables
models.Base.metadata.create_all(bind=db.engine)


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

@app.get("/")
async def health():
    return {"status": "Healthy!"}

