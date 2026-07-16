from typing import Optional
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
