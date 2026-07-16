from typing import Optional, List
import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    """
    Groups songs and models into a single workspace.
    """
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active") # active, archived
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="projects")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="projects")
    songs: Mapped[List["Song"]] = relationship("Song", back_populates="project", cascade="all, delete-orphan")
    timeline_events: Mapped[List["ProjectEvent"]] = relationship("ProjectEvent", back_populates="project", cascade="all, delete-orphan", order_by="ProjectEvent.created_at")
