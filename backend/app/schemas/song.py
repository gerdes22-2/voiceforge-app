from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

class SongBase(BaseModel):
    pass

class SongRead(SongBase):
    id: uuid.UUID
    project_id: uuid.UUID
    original_file_uuid: uuid.UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
