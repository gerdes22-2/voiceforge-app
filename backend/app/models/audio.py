from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Song(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "songs"
    """
    Represents an uploaded audio track to be processed.
    """
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    file_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_assets.id", ondelete="RESTRICT"), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    
    # Extracted Audio Characteristics
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    musical_key: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    loudness_lufs: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    peak_level_db: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="songs")
    file_asset: Mapped["FileAsset"] = relationship("FileAsset")
    processing_jobs: Mapped[List["ProcessingJob"]] = relationship("ProcessingJob", back_populates="song", cascade="all, delete-orphan")

class AudioCache(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "audio_cache"
    hash_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    generation_params: Mapped[dict] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
