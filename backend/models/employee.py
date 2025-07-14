from pydantic import BaseModel,EmailStr
from datetime import date
from typing import Optional

class Employee(BaseModel):
    user_id: str
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
    status: str = "Active"
    reporting_manager_id: Optional[str]
    reporting_manager: Optional[str] = None