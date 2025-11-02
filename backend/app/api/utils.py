from fastapi import APIRouter, HTTPException, status, Depends, Cookie
from fastapi.responses import JSONResponse
from app import schemas, models
from app.db import get_db
from app.api.authentication import SECRET_KEY, ALGORITHM
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt


async def get_current_user(db: Session = Depends(get_db), access_token: str = Cookie(None)):

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No Token Found")
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(models.User).filter(models.User.username == username).first()

        return user
    
    except Exception as e:
        # print("\n\n\n")
        # print(e)
        # print("\n\n\n")
        raise HTTPException(status_code=401, detail=f"Token verification failed.\n\n{str(e)}")
