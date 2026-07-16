import os

os.makedirs("backend/app/models", exist_ok=True)
os.makedirs("backend/app/crud", exist_ok=True)
os.makedirs("backend/app/schemas", exist_ok=True)
os.makedirs("backend/app/services", exist_ok=True)

# 1. Models
with open("backend/app/models/base.py", "w") as f:
    f.write("""import uuid
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
    \"\"\"Provides created_at and updated_at timezone-aware timestamps.\"\"\"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

class SoftDeleteMixin:
    \"\"\"Provides soft delete capabilities.\"\"\"
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

class UUIDMixin:
    \"\"\"Provides a UUIDv7 primary key for time-sortable IDs.\"\"\"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)
""")

with open("backend/app/models/enums.py", "w") as f:
    f.write("""import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ARTIST = "artist"
    MANAGER = "manager"
    PRODUCER = "producer"

class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class JobType(str, enum.Enum):
    STEM_SEPARATION = "stem_separation"
    VOICE_CONVERSION = "voice_conversion"
    AUDIO_ANALYSIS = "audio_analysis"
    TRAINING = "training"
""")

with open("backend/app/models/user.py", "w") as f:
    f.write("""from typing import Optional, List
from sqlalchemy import String, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from .enums import UserRole

class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    \"\"\"
    Represents a platform user.
    Indexes: email (unique)
    \"\"\"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.ARTIST, nullable=False)
    profile_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    projects: Mapped[List["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    voice_datasets: Mapped[List["VoiceDataset"]] = relationship("VoiceDataset", back_populates="user", cascade="all, delete-orphan")
    voice_models: Mapped[List["VoiceModel"]] = relationship("VoiceModel", back_populates="user", cascade="all, delete-orphan")
    usage_logs: Mapped[List["UsageLog"]] = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
""")

with open("backend/app/models/project.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    \"\"\"
    Groups songs and models into a single workspace.
    Indexes: user_id
    \"\"\"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="projects")
    songs: Mapped[List["Song"]] = relationship("Song", back_populates="project", cascade="all, delete-orphan")
""")

with open("backend/app/models/audio.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Song(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "songs"
    \"\"\"
    Represents an uploaded audio track to be processed.
    \"\"\"
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    original_file_uuid: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="songs")
    processing_jobs: Mapped[List["ProcessingJob"]] = relationship("ProcessingJob", back_populates="song", cascade="all, delete-orphan")

class AudioCache(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "audio_cache"
    \"\"\"
    Caches intermediate audio artifacts to save redundant processing.
    \"\"\"
    hash_key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(100), nullable=False) # stem, transcription, etc.
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    generation_params: Mapped[dict] = mapped_column(JSON, nullable=False)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
""")

with open("backend/app/models/voice.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from sqlalchemy import String, ForeignKey, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class VoiceDataset(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_datasets"
    \"\"\"
    A collection of audio samples for a specific voice.
    \"\"\"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="voice_datasets")
    versions: Mapped[List["VoiceDatasetVersion"]] = relationship("VoiceDatasetVersion", back_populates="dataset", cascade="all, delete-orphan")

class VoiceDatasetVersion(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_dataset_versions"
    \"\"\"
    A specific immutable version of a Voice Dataset.
    \"\"\"
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voice_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    file_uuids: Mapped[List[str]] = mapped_column(JSON, nullable=False) # List of file references
    total_duration_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    dataset: Mapped["VoiceDataset"] = relationship("VoiceDataset", back_populates="versions")
    voice_models: Mapped[List["VoiceModel"]] = relationship("VoiceModel", back_populates="dataset_version")

class VoiceModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_models"
    \"\"\"
    A trained AI Voice Model derived from a dataset version.
    \"\"\"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("voice_dataset_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(100), nullable=False) # rvc, seed-vc
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="created")
    file_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    training_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="voice_models")
    dataset_version: Mapped[Optional["VoiceDatasetVersion"]] = relationship("VoiceDatasetVersion", back_populates="voice_models")
    training_jobs: Mapped[List["TrainingJob"]] = relationship("TrainingJob", back_populates="voice_model")
""")

with open("backend/app/models/job.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Float, Integer, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from .enums import JobStatus, JobType

class ProcessingJob(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "processing_jobs"
    __table_args__ = (
        Index('ix_processing_jobs_song_id_status', 'song_id', 'status'),
    )
    \"\"\"
    Tracks inference and processing tasks (e.g., Stem Separation).
    \"\"\"
    song_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    worker_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    result_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    song: Mapped["Song"] = relationship("Song", back_populates="processing_jobs")
    benchmarks: Mapped[List["JobBenchmark"]] = relationship("JobBenchmark", back_populates="processing_job", cascade="all, delete-orphan")
    exports: Mapped[List["Export"]] = relationship("Export", back_populates="job", cascade="all, delete-orphan")

class TrainingJob(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "training_jobs"
    \"\"\"
    Tracks voice model training tasks.
    \"\"\"
    voice_model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voice_models.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    worker_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    epochs_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    epochs_completed: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    voice_model: Mapped["VoiceModel"] = relationship("VoiceModel", back_populates="training_jobs")
    benchmarks: Mapped[List["JobBenchmark"]] = relationship("JobBenchmark", back_populates="training_job", cascade="all, delete-orphan")

class JobBenchmark(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_benchmarks"
    \"\"\"
    Records detailed telemetry, performance, and quality metrics for jobs.
    \"\"\"
    processing_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("processing_jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    training_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("training_jobs.id", ondelete="CASCADE"), nullable=True, index=True)
    
    provider_used: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    runtime_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    gpu_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    vram_used_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_score: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    processing_cost_est: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    output_durations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fallback_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    processing_job: Mapped[Optional["ProcessingJob"]] = relationship("ProcessingJob", back_populates="benchmarks")
    training_job: Mapped[Optional["TrainingJob"]] = relationship("TrainingJob", back_populates="benchmarks")

class Export(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "exports"
    \"\"\"
    Tracks generated files available for user download.
    \"\"\"
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("processing_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    job: Mapped["ProcessingJob"] = relationship("ProcessingJob", back_populates="exports")
""")

with open("backend/app/models/system.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, JSON, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin

class Settings(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "settings"
    \"\"\"Global application configuration stored in DB\"\"\"
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    value: Mapped[dict] = mapped_column(JSON, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

class FeatureFlag(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "feature_flags"
    \"\"\"Toggles for new features\"\"\"
    key: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollout_percentage: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

class ProviderRegistry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "provider_registry"
    \"\"\"Registered AI capabilities and orchestrators\"\"\"
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    supported_task_types: Mapped[List[str]] = mapped_column(JSON, nullable=False)

    models: Mapped[List["AIModel"]] = relationship("AIModel", back_populates="provider")

class ModelRegistry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "model_registry"
    \"\"\"Metadata for specific model versions\"\"\"
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    models: Mapped[List["AIModel"]] = relationship("AIModel", back_populates="registry_info")

class AIModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_models"
    \"\"\"Specific AI model instantiations deployed\"\"\"
    provider_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("provider_registry.id", ondelete="CASCADE"), nullable=False)
    registry_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("model_registry.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    memory_req_mb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    provider: Mapped["ProviderRegistry"] = relationship("ProviderRegistry", back_populates="models")
    registry_info: Mapped["ModelRegistry"] = relationship("ModelRegistry", back_populates="models")

class GPUWorker(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "gpu_workers"
    \"\"\"Tracks active workers\"\"\"
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    gpu_type: Mapped[str] = mapped_column(String(100), nullable=False)
    vram_total: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    last_heartbeat: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class JobQueueMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_queue_metrics"
    \"\"\"Periodic snapshots of queue health\"\"\"
    queue_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pending_count: Mapped[int] = mapped_column(Integer, nullable=False)
    active_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_wait_time_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
""")

with open("backend/app/models/log.py", "w") as f:
    f.write("""from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin

class UsageLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "usage_logs"
    \"\"\"Billing and quota tracking\"\"\"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("processing_jobs.id", ondelete="SET NULL"), nullable=True, index=True)
    gpu_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cpu_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    storage_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user: Mapped["User"] = relationship("User", back_populates="usage_logs")

class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    \"\"\"Security and compliance events\"\"\"
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"
    \"\"\"User alerts (e.g., job completed)\"\"\"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notifications")
""")

with open("backend/app/models/__init__.py", "w") as f:
    f.write("""from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from .enums import UserRole, JobStatus, JobType, ProviderType
from .user import User
from .project import Project
from .audio import Song, AudioCache
from .voice import VoiceDataset, VoiceDatasetVersion, VoiceModel
from .job import ProcessingJob, TrainingJob, JobBenchmark, Export
from .system import Settings, FeatureFlag, ProviderRegistry, ModelRegistry, AIModel, GPUWorker, JobQueueMetric
from .log import UsageLog, AuditLog, Notification

__all__ = [
    "Base", "UUIDMixin", "TimestampMixin", "SoftDeleteMixin",
    "UserRole", "JobStatus", "JobType", "ProviderType",
    "User", "Project", "Song", "AudioCache",
    "VoiceDataset", "VoiceDatasetVersion", "VoiceModel",
    "ProcessingJob", "TrainingJob", "JobBenchmark", "Export",
    "Settings", "FeatureFlag", "ProviderRegistry", "ModelRegistry", "AIModel", "GPUWorker", "JobQueueMetric",
    "UsageLog", "AuditLog", "Notification"
]
""")

# Also delete the old schema.py
if os.path.exists("backend/app/models/schema.py"):
    os.remove("backend/app/models/schema.py")

