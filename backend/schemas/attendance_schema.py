from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from typing import Optional

class AttendanceStatus(str, Enum):
    NOT_MARKED = "Not Marked"
    PRESENT = "Present"
    ABSENT = "Absent"

class Attendance(BaseModel):
    id: str
    user_id: str
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    break_in: Optional[datetime] = None
    break_out: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.NOT_MARKED
    total_hours: Optional[float] = None 
    employee_name: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True