from datetime import datetime
from pydantic import BaseModel,Field
from typing import List,Optional

class Comment(BaseModel):
    user_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Task(BaseModel):
    title: str
    description: str
    assigned_to: List[str]
    assigned_by: str
    status: str = "Pending"
    priority: str = "Normal"
    due_date: Optional[datetime] = None
    created_at: str = Field(default_factory=datetime.utcnow)
    updated_at: str = Field(default_factory=datetime.utcnow)
    comments: List[Comment] = []