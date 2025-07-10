from pydantic import BaseModel,EmailStr

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str
    