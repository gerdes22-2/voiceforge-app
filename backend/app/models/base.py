import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid7 import uuid7

class Base(DeclarativeBase):
    pass

def utcnow():
    return datetime.now(timezone.utc)

class TimestampMixin:
    """Provides created_at and updated_at timezone-aware timestamps."""
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

class SoftDeleteMixin:
    """Provides soft delete capabilities."""
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

class UUIDMixin:
    """Provides a UUIDv7 primary key for time-sortable IDs."""
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
