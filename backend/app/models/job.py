from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey, JSON, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class ProcessingJob(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "processing_jobs"
    song_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    song: Mapped["Song"] = relationship("Song", back_populates="processing_jobs")

class TrainingJob(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "training_jobs"
    voice_model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voice_models.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    voice_model: Mapped["VoiceModel"] = relationship("VoiceModel", back_populates="training_jobs")

class JobBenchmark(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_benchmarks"
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_sec: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

class Export(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "exports"
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    file_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_assets.id", ondelete="CASCADE"), nullable=False)
