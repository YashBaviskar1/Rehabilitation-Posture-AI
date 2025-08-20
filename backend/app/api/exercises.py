from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app import schemas, models
from app.db import get_db
from app.api.utils import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/exercises")



@router.get("/")
async def get_all_exercises(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")

    exercises = db.query(models.Exercises).all()

    exercises_list = [
        {
            "id": exercise.id,
            "title": exercise.title
        } for exercise in exercises
    ]

    return exercises_list



@router.post("/create")
async def create_new_exercise(request_data: schemas.Create_Exercise, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")
    
    if not request_data.title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title not provided")

    new_exercise = models.Exercises(title = request_data.title)

    try:
        #add new user to db
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        
        return JSONResponse({"status":"ok"})
    
    except IntegrityError as e:
        db.rollback()
        #Handle if title already exists
        if request_data.title in str(e):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Title already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Some Integrity error Occurred"
            )
            
    except Exception as e:
        db.rollback()
        #handle exceptions that may occur.
        print(f"\n\nError in exercise creation:\n{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.post("/assign")
async def assign_exercise_to_patient(request_data: schemas.Assign_Exercise, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")
    
    #Make sure the user exists with the given ID exists and is a patient 
    patient = db.query(models.User).filter(models.User.id == request_data.patient_id).first()
    if not patient or patient.role == "doctor":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient found with given ID")
    
    
    try:
        #Assign all exercises if they exist
        for exercise_id in request_data.exercise_ids:
            exercise = db.query(models.Exercises).filter(models.Exercises.id == exercise_id).first()
            #Make sure the exercises exist
            if not exercise:
                #Possible wrong error code due to being in try block...
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No exercise found with given ID: {exercise_id}")
            
            new_entry = models.User_Exercises(
                user_id = patient.id,
                exercise_id = exercise.id,
            )

            db.add(new_entry)

        #commit changes
        db.commit()
        return JSONResponse({"status":"ok"})
            
    except Exception as e:
        db.rollback()
        #handle exceptions that may occur.
        print(f"\n\nError in exercise assignment:\n{str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
