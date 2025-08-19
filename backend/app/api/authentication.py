from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import JSONResponse
from app import schemas, models
from app.db import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt

router = APIRouter(prefix="/auth")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# SECRET and Config
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


#Function to create access token with details
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to hash a password
def hash_password(password: str) -> str:
    return password_context.hash(password)





@router.get("/logout")
async def logout():

    response = JSONResponse({"status": "ok"})
    response.delete_cookie("access_token")

    return response



@router.post("/login")
async def login(request_data: schemas.Login_Request, db: Session = Depends(get_db)):
   
   #Authenticate user
    user = db.query(models.User).filter(models.User.username == request_data.username).first()

    if not user or not password_context.verify(request_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password :-("
        )
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    response = JSONResponse(content={"access_token": access_token})
    response.status_code = status.HTTP_200_OK
    response.set_cookie(
        key="access_token",
        value=access_token,
        samesite="strict",
        httponly=True,
        secure=True
    )
    
    return response



@router.post("/register")
async def register(request_data: schemas.Register_Request, db:Session = Depends(get_db)):
    
    #check if username and password is provided
    if not request_data.username or not request_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or password not provided"
        )

    #check if role is correct 
    if request_data.role != "doctor" and request_data.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect role provided"
        )
    
    #create new user
    new_user = models.User(
        username = request_data.username,
        password = hash_password(request_data.password),
        role = request_data.role,
    )

    try:
        #add new user to db
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    
    except IntegrityError as e:
        db.rollback()
        #Handle if username already taken
        if request_data.username in str(e):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username taken"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Integrity error"
            )
            
    except Exception as e:
        db.rollback()
        #handle exceptions that mat occur. Eg username taken
        print(f"\n\nError in registration:\n{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return JSONResponse({"status": "ok"}, status_code=status.HTTP_200_OK)