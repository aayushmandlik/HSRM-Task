from pydantic import BaseModel,Field
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
    id: str = Field(..., alias="_id")
    employee_id: str
    employee_name: str  
    start_date: date
    end_date: date
    leave_type: str
    reason: str
    status: LeaveStatus
    days: int
    created_at: datetime
    updated_at: datetime
    leave_taken: int = 0
    remaining_leaves: int = 20
    approved_by: Optional[str] = None 

    class Config:
        orm_mode = True

class LeaveUpdateStatus(BaseModel):
    status: LeaveStatus
    approved_by: str

class LeaveUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    leave_type: Optional[str] = None
    reason: Optional[str] = None
