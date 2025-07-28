from datetime import datetime
from pydantic import BaseModel
from typing import List,Optional

class commentSchema(BaseModel):
    user_id: str
    message: str
    timestamp: Optional[datetime] = None

class TaskCreate(BaseModel):
    title: str
    description: str
    assigned_to: List[str]
    assigned_by: str
    priority: str = "Normal"
    due_date: Optional[datetime] = None
    status: str
    project: str
    
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[List[str]] = None
    assigned_by: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    project: Optional[str] = None


class TaskUpdateStatus(BaseModel):
    status: str

class TaskComment(BaseModel):
    user_id: str
    message: str

class TaskOut(BaseModel):
    id: str
    title: str
    description: str
    assigned_to: List[str]
    assigned_by: str
    status: str
    priority: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    comments: List[commentSchema] = [],
    project: Optional[str]