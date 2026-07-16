from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin

class ProjectEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_events"
    """
    Immutable event history for a project.
    """
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'song_uploaded', 'stem_separation_started'
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="timeline_events")
