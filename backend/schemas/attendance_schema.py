from pydantic import BaseModel
from datetime import datetime


class Attendance(BaseModel):
    id: str
    check_in: datetime
    checl_out: datetime