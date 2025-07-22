from pydantic import BaseModel
from datetime import datetime


class Attendance(BaseModel):
    id: str
    check_in: datetime
    check_out: datetime