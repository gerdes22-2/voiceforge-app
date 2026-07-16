import os

# Create necessary directories
os.makedirs("backend/app/models", exist_ok=True)
os.makedirs("backend/app/crud", exist_ok=True)
os.makedirs("backend/app/schemas", exist_ok=True)
os.makedirs("backend/app/services", exist_ok=True)
os.makedirs("backend/app/api/v1", exist_ok=True)

# 1. Update Project Model
with open("backend/app/models/project.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Project(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "projects"
    \"\"\"
    Groups songs and models into a single workspace.
    \"\"\"
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
""")

# 2. Add ProjectEvent for Immutable Timeline
with open("backend/app/models/timeline.py", "w") as f:
    f.write("""from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin

class ProjectEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "project_events"
    \"\"\"
    Immutable event history for a project.
    \"\"\"
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'song_uploaded', 'stem_separation_started'
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_info: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="timeline_events")
""")

# 3. Add FileAsset for Storage Management
with open("backend/app/models/storage.py", "w") as f:
    f.write("""from typing import Optional
import uuid
from sqlalchemy import String, ForeignKey, Integer, Float, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class FileAsset(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "file_assets"
    \"\"\"
    Universal tracker for any uploaded or generated file.
    \"\"\"
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
""")

# 4. Update Song Model to link FileAsset and advanced Metadata
with open("backend/app/models/audio.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class Song(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "songs"
    \"\"\"
    Represents an uploaded audio track to be processed.
    \"\"\"
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
""")

# 5. Add VoiceDatasetCategory logic
with open("backend/app/models/voice.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from sqlalchemy import String, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class VoiceDataset(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_datasets"
    \"\"\"
    A collection of structured audio samples for a specific voice.
    \"\"\"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="voice_datasets")
    versions: Mapped[List["VoiceDatasetVersion"]] = relationship("VoiceDatasetVersion", back_populates="dataset", cascade="all, delete-orphan")
    items: Mapped[List["VoiceDatasetItem"]] = relationship("VoiceDatasetItem", back_populates="dataset", cascade="all, delete-orphan")

class VoiceDatasetItem(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_dataset_items"
    \"\"\"
    Individual structured recording inside a dataset.
    Categories: Speech, Singing, Rap, Harmony, Falsetto, Emotion, Scales, Sustained Notes.
    \"\"\"
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voice_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_asset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("file_assets.id", ondelete="RESTRICT"), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False) 
    emotion_tag: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    dataset: Mapped["VoiceDataset"] = relationship("VoiceDataset", back_populates="items")
    file_asset: Mapped["FileAsset"] = relationship("FileAsset")

class VoiceDatasetVersion(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_dataset_versions"
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voice_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    version_tag: Mapped[str] = mapped_column(String(50), nullable=False)
    file_uuids: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    total_duration_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    dataset: Mapped["VoiceDataset"] = relationship("VoiceDataset", back_populates="versions")
    voice_models: Mapped[List["VoiceModel"]] = relationship("VoiceModel", back_populates="dataset_version")

class VoiceModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_models"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("voice_dataset_versions.id", ondelete="SET NULL"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="created")
    file_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    training_metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="voice_models")
    dataset_version: Mapped[Optional["VoiceDatasetVersion"]] = relationship("VoiceDatasetVersion", back_populates="voice_models")
    training_jobs: Mapped[List["TrainingJob"]] = relationship("TrainingJob", back_populates="voice_model")
""")

# 6. Rebuild __init__.py
with open("backend/app/models/__init__.py", "w") as f:
    f.write("""from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from .enums import UserRole, JobStatus, JobType
from .iam import Organization, OrganizationMember, RefreshToken, RolePermission
from .user import User
from .project import Project
from .timeline import ProjectEvent
from .storage import FileAsset
from .audio import Song, AudioCache
from .voice import VoiceDataset, VoiceDatasetItem, VoiceDatasetVersion, VoiceModel
from .job import ProcessingJob, TrainingJob, JobBenchmark, Export
from .system import Settings, FeatureFlag, ProviderRegistry, ModelRegistry, AIModel, GPUWorker, JobQueueMetric
from .log import UsageLog, AuditLog, Notification

__all__ = [
    "Base", "UUIDMixin", "TimestampMixin", "SoftDeleteMixin",
    "UserRole", "JobStatus", "JobType",
    "Organization", "OrganizationMember", "RefreshToken", "RolePermission",
    "User", "Project", "ProjectEvent", "FileAsset", "Song", "AudioCache",
    "VoiceDataset", "VoiceDatasetItem", "VoiceDatasetVersion", "VoiceModel",
    "ProcessingJob", "TrainingJob", "JobBenchmark", "Export",
    "Settings", "FeatureFlag", "ProviderRegistry", "ModelRegistry", "AIModel", "GPUWorker", "JobQueueMetric",
    "UsageLog", "AuditLog", "Notification"
]
""")

