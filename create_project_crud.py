import os

with open("backend/app/schemas/project.py", "w") as f:
    f.write("""from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str = "active"

class ProjectCreate(ProjectBase):
    organization_id: Optional[UUID] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class ProjectRead(ProjectBase):
    id: UUID
    organization_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
""")

with open("backend/app/crud/crud_project.py", "w") as f:
    f.write("""from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    async def get_multi_by_user(self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Project]:
        query = select(Project).where(Project.user_id == user_id, Project.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_multi_by_organization(self, db: AsyncSession, *, organization_id: UUID, skip: int = 0, limit: int = 100) -> List[Project]:
        query = select(Project).where(Project.organization_id == organization_id, Project.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    async def create_with_owner(self, db: AsyncSession, *, obj_in: ProjectCreate, user_id: UUID) -> Project:
        obj_in_data = obj_in.model_dump()
        db_obj = Project(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

project = CRUDProject(Project)
""")

# Also create timeline schemas and CRUD
with open("backend/app/schemas/timeline.py", "w") as f:
    f.write("""from typing import Optional
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
""")

with open("backend/app/crud/crud_timeline.py", "w") as f:
    f.write("""from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.timeline import ProjectEvent

class CRUDTimeline:
    async def create(self, db: AsyncSession, *, project_id: UUID, event_type: str, description: str, metadata_info: dict = None) -> ProjectEvent:
        event = ProjectEvent(
            project_id=project_id,
            event_type=event_type,
            description=description,
            metadata_info=metadata_info
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    async def get_by_project(self, db: AsyncSession, *, project_id: UUID) -> List[ProjectEvent]:
        query = select(ProjectEvent).where(ProjectEvent.project_id == project_id).order_by(ProjectEvent.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

timeline = CRUDTimeline()
""")
