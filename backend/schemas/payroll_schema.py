from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class PayrollCreate(BaseModel):
    employee_id: str
    email: str
    basic_salary: float
    bonus: float = 0.0
    deductions: float = 0.0
    pay_period_start: date
    pay_period_end: date
    description: Optional[str] = None

class PayrollResponse(BaseModel):
    _id: str
    employee_id: str
    email: str
    basic_salary: float
    bonus: float
    deductions: float
    net_salary: float
    pay_period_start: datetime
    pay_period_end: datetime
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PayrollUpdate(BaseModel):
    basic_salary: Optional[float]
    bonus: Optional[float]
    deductions: Optional[float]
    pay_period_start: Optional[date]
    pay_period_end: Optional[date]
    description: Optional[str]
    status: Optional[str]