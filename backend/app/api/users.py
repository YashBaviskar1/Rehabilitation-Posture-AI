from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from app import schemas, models
from app.db import get_db
from app.api.utils import get_current_user
from sqlalchemy.orm import Session



router = APIRouter(prefix="/users")





@router.get("/patients")
async def get_patients_list(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")

    all_user_objects = db.query(models.User).filter(models.User.role == "patient").all()

    all_user_list = []
    for patient in all_user_objects:
        #Serialise exercises for current patient
        patient_exercises = [
            {
                "id": ass.exercise.id,
                "title": ass.exercise.title,
            }
            for ass in patient.assignments
        ]
        #Create and add patient to list by serialising
        all_user_list.append({
                "id": patient.id,
                "username": patient.username,
                "age": patient.age or "NA",
                "exercises" : patient_exercises
            })

    return JSONResponse(all_user_list)



@router.get("/patients/me")
async def get_patient_profile(user: models.User = Depends(get_current_user)):

    if user.role != "patient":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient found with given ID")
    
    patient_exercises = [
            {
                "id": ass.exercise.id,
                "title": ass.exercise.title,
            }
            for ass in user.assignments
        ]

    response = JSONResponse({
            "id": user.id,
            "username": user.username,
            "age": user.age,
            "exercises": patient_exercises
            })

    return response



@router.put("/patients/me")
async def update_patient_profile(request_data: schemas.Update_User, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    try:
        user.age = request_data.age

        db.commit()
        db.refresh(user)

        return JSONResponse({"status": "ok"})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Something went wrong.\n {str(e)}")



@router.get("/patients/{patient_id}")
async def get_patient_by_id(patient_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if not patient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient ID not provided")

    if user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")


    patient: models.User = db.query(models.User).filter(models.User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient found with given ID")
    if patient.role != "patient":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No patient found with given ID")


    patient_exercises = [
            {
                "id": ass.exercise.id,
                "title": ass.exercise.title,
            }
            for ass in patient.assignments
        ]


    response = JSONResponse({
            "id": patient.id,
            "username": patient.username,
            "role": patient.role,
            "exercises": patient_exercises
         })

    return response


@router.get("/doctors")
async def get_doctors_list(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):

    if user.role != "doctor":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorised for this")

    all_user_objects = db.query(models.User).filter(models.User.role == "doctor").all()

    all_user_list = [
        {
            "id": doctor.id,
            "username": doctor.username,
            "age": doctor.age
        } for doctor in all_user_objects
    ]

    return JSONResponse(all_user_list)


