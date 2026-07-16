from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ProjectEventBase(BaseModel):
    event_type: str
    description: str
    metadata_info: Optional[dict] = None

class ProjectEventCreate(ProjectEventBase):
    project_id: UUID

class ProjectEventRead(ProjectEventBase):
    id: UUID
    project_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
