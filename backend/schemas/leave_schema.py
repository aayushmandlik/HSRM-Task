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
    employee_name: str  # Added for admin identification
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
    approved_by: Optional[str] = None  # Added to track who approved the leave

    class Config:
        orm_mode = True

class LeaveUpdate(BaseModel):
    status: LeaveStatus