from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app import schemas, models
from app.db import get_db
from app.api.utils import get_current_user
from sqlalchemy.orm import Session



router = APIRouter(prefix="/users")

@router.get("/me")
async def get_profile(user: models.User = Depends(get_current_user)):

    response = JSONResponse({"id": user.id, "username": user.username, "role": user.role})

    return response





