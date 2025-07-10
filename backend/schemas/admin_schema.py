from pydantic import BaseModel,EmailStr

class AdminRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    code: str

class AdminLogin(BaseModel):
    email: EmailStr
    password: str