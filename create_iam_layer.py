import os

os.makedirs("backend/app/models", exist_ok=True)
os.makedirs("backend/app/crud", exist_ok=True)
os.makedirs("backend/app/schemas", exist_ok=True)
os.makedirs("backend/app/services", exist_ok=True)
os.makedirs("backend/app/api/v1", exist_ok=True)
os.makedirs("backend/tests/unit", exist_ok=True)
os.makedirs("backend/tests/integration", exist_ok=True)

# Update Enums for IAM
with open("backend/app/models/enums.py", "w") as f:
    f.write("""import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ARTIST = "artist"
    MANAGER = "manager"
    PRODUCER = "producer"
    VIEWER = "viewer"

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

# Create IAM models (Organizations, Members, Tokens, Permissions)
with open("backend/app/models/iam.py", "w") as f:
    f.write("""from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from .enums import UserRole

class Organization(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organizations"
    \"\"\"Root entity for workspaces\"\"\"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    billing_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    members: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="organization", cascade="all, delete-orphan")

class OrganizationMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organization_members"
    \"\"\"Link between User and Organization with a specific role\"\"\"
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.VIEWER, nullable=False)
    
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="organization_memberships")

class RefreshToken(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"
    \"\"\"Stores refresh tokens for token rotation and session management\"\"\"
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

class RolePermission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "role_permissions"
    \"\"\"Defines what actions each role can perform\"\"\"
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 'project', 'voice_model'
    action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 'create', 'delete', 'train'
""")

# Update User model
with open("backend/app/models/user.py", "w") as f:
    f.write("""from typing import Optional, List
from sqlalchemy import String, JSON, Enum, Boolean, Integer, DateTime
from datetime import datetime
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
    password_hash: Mapped[str] = mapped_column(String(255), nullable=True) # Nullable for OAuth-only users
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Security fields
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    profile_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    organization_memberships: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    voice_datasets: Mapped[List["VoiceDataset"]] = relationship("VoiceDataset", back_populates="user", cascade="all, delete-orphan")
    voice_models: Mapped[List["VoiceModel"]] = relationship("VoiceModel", back_populates="user", cascade="all, delete-orphan")
    usage_logs: Mapped[List["UsageLog"]] = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
""")

# Update Project model to support Organizations
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
    \"\"\"
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True) # Fallback for personal projects
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="projects")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="projects")
    songs: Mapped[List["Song"]] = relationship("Song", back_populates="project", cascade="all, delete-orphan")
""")

# Update models __init__.py
with open("backend/app/models/__init__.py", "w") as f:
    f.write("""from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from .enums import UserRole, JobStatus, JobType
from .iam import Organization, OrganizationMember, RefreshToken, RolePermission
from .user import User
from .project import Project
from .audio import Song, AudioCache
from .voice import VoiceDataset, VoiceDatasetVersion, VoiceModel
from .job import ProcessingJob, TrainingJob, JobBenchmark, Export
from .system import Settings, FeatureFlag, ProviderRegistry, ModelRegistry, AIModel, GPUWorker, JobQueueMetric
from .log import UsageLog, AuditLog, Notification

__all__ = [
    "Base", "UUIDMixin", "TimestampMixin", "SoftDeleteMixin",
    "UserRole", "JobStatus", "JobType",
    "Organization", "OrganizationMember", "RefreshToken", "RolePermission",
    "User", "Project", "Song", "AudioCache",
    "VoiceDataset", "VoiceDatasetVersion", "VoiceModel",
    "ProcessingJob", "TrainingJob", "JobBenchmark", "Export",
    "Settings", "FeatureFlag", "ProviderRegistry", "ModelRegistry", "AIModel", "GPUWorker", "JobQueueMetric",
    "UsageLog", "AuditLog", "Notification"
]
""")

