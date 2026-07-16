from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class JobBase(BaseModel):
    task_type: str
    
class JobCreate(JobBase):
    song_id: uuid.UUID
    
class JobRead(JobBase):
    id: uuid.UUID
    song_id: Optional[uuid.UUID]
    status: str
    progress: float
    created_at: datetime
    
    class Config:
        from_attributes = True
