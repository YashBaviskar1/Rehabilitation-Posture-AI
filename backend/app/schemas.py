from pydantic import BaseModel

class Login_Request(BaseModel):
    username: str
    password: str

class Register_Request(BaseModel):
    username: str
    password: str
    role: str