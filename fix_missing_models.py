import os

with open("backend/app/models/job.py", "w") as f:
    f.write("""from typing import Optional
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
""")

with open("backend/app/models/system.py", "w") as f:
    f.write("""from typing import Optional
import uuid
from sqlalchemy import String, JSON, Boolean, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, UUIDMixin, TimestampMixin

class Settings(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "system_settings"
    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    value: Mapped[JSON] = mapped_column(JSON, nullable=False)

class FeatureFlag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "feature_flags"
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

class ProviderRegistry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "provider_registry"
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    capabilities: Mapped[JSON] = mapped_column(JSON, nullable=False)

class ModelRegistry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "model_registry"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    checkpoint_hash: Mapped[str] = mapped_column(String(100), nullable=False)

class AIModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_models"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
class GPUWorker(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gpu_workers"
    hostname: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    gpu_type: Mapped[str] = mapped_column(String(100), nullable=False)
    total_vram_mb: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="offline")

class JobQueueMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_queue_metrics"
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    queue_name: Mapped[str] = mapped_column(String(100), nullable=False)
    active_jobs: Mapped[int] = mapped_column(Integer, nullable=False)
    pending_jobs: Mapped[int] = mapped_column(Integer, nullable=False)
    failed_jobs: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_wait_time_sec: Mapped[float] = mapped_column(Float, nullable=False)
""")

with open("backend/app/models/log.py", "w") as f:
    f.write("""from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, UUIDMixin, TimestampMixin

class UsageLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "usage_logs"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False)
""")

# Recreate enums model just in case it missed some
with open("backend/app/models/enums.py", "w") as f:
    f.write("""import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ARTIST = "artist"
    PRODUCER = "producer"
    GUEST = "guest"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, enum.Enum):
    STEM_SEPARATION = "stem_separation"
    VOICE_TRAINING = "voice_training"
    VOICE_CONVERSION = "voice_conversion"
    MASTERING = "mastering"
""")
