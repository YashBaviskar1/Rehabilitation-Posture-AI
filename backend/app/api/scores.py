from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app import schemas, models
from app.db import get_db
from app.api.utils import get_current_user
from sqlalchemy.orm import Session



router = APIRouter(prefix="/scores")

@router.get("/patient/{patient_id}")
async def get_patient_score(patient_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):


    if not patient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient ID not provided")

    patient: models.User = db.query(models.User).filter(models.User.id == patient_id).first()
    print(user.role, patient.id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient found with given ID")
    if patient.role != "patient":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient found with given ID")

    if user.role != "doctor" and user.id != patient.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")
    
    scores: list[models.UserExerciseScore] = (
        db.query(models.UserExerciseScore)
            .filter(models.UserExerciseScore.user_id == patient_id)
            .order_by(models.UserExerciseScore.timestamp.desc())
            .limit(7)
            .all()
        )

    return [{"timestamp": sc.timestamp, "score": sc.score, "exercise": sc.exercise.title} for sc in scores][::-1]

@router.post("/add")
async def store_patient_score(request_data: schemas.Add_New_Score, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    patient: models.User = db.query(models.User).filter(models.User.id == request_data.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient found with given ID")
    # if user.role != "doctor":
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You are not authorised for this")

    if user.role != "doctor" and user.id != patient.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")
    
    try:
        new_score = models.UserExerciseScore(
            user_id=request_data.patient_id,
            exercise_id=request_data.exercise_id,
            score=request_data.score,
            timestamp=request_data.timestamp,
        )

        db.add(new_score)
        db.commit()
        db.refresh(new_score)
    
    except Exception as e:
        db.rollback()
        #handle exceptions that may occur.
        print(f"\n\nError in score assignment:\n{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    return JSONResponse({"status":"ok"})
