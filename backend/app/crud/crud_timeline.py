from typing import List
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
