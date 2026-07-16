from typing import Optional, List
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
