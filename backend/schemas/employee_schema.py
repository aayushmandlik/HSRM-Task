from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class EmployeeCreate(BaseModel):
    # user_id: str
    emp_code: str
    name: str
    email: EmailStr
    phone: str
    gender: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None
    department: str
    designation: str
    date_of_joining: str
    location: str
    reporting_manager_id: Optional[str]
    reporting_manager: Optional[str] = None
    status: str

class EmployeeUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    gender: Optional[str]
    dob: Optional[str]
    address: Optional[str]
    profile_image: Optional[str]
    department: Optional[str]
    designation: Optional[str]
    date_of_joining: Optional[str]
    location: Optional[str]
    reporting_manager_id: Optional[str]
    reporting_manager: Optional[str]
    status: str

class EmployeeOut(EmployeeCreate):
    _id: str
    status: str