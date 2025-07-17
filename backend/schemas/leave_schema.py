from pydantic import BaseModel
from datetime import date, datetime
from enum import Enum
from typing import Optional

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class LeaveCreate(BaseModel):
    start_date: date
    end_date: date
    leave_type: str
    reason: str

class LeaveResponse(BaseModel):
    _id: str
    employee_id: str
    start_date: date
    end_date: date
    leave_type: str
    reason: str
    status: LeaveStatus
    days: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LeaveUpdate(BaseModel):
    status: LeaveStatus