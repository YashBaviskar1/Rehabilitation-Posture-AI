from pydantic import BaseModel

class Login_Request(BaseModel):
    username: str
    password: str

class Register_Request(BaseModel):
    name: str
    username: str
    password: str
    role: str

class Update_User(BaseModel):
    age: int | None

class Create_Exercise(BaseModel):
    title: str

class Assign_Exercise(BaseModel):
    patient_id: int
    exercise_ids: list[int]

class Deassign_Exercise(BaseModel):
    patient_id: int
    exercise_ids: list[int]