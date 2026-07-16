from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey, Integer, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class FileAsset(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "file_assets"
    """
    Universal tracker for any uploaded or generated file.
    """
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="local") # local, s3, r2, minio
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    
    # Audio Specific Metadata
    duration_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    channels: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bit_depth: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Validation & Security
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    virus_scan_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # pending, clean, infected

    user: Mapped["User"] = relationship("User")
