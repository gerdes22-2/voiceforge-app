from typing import Optional, List
import uuid
from sqlalchemy import String, ForeignKey, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin

class VoiceDataset(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_datasets"
    """
    A collection of structured audio samples for a specific voice.
    """
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="voice_datasets")
    versions: Mapped[List["VoiceDatasetVersion"]] = relationship("VoiceDatasetVersion", back_populates="dataset", cascade="all, delete-orphan")
    items: Mapped[List["VoiceDatasetItem"]] = relationship("VoiceDatasetItem", back_populates="dataset", cascade="all, delete-orphan")

class VoiceDatasetItem(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "voice_dataset_items"
    """
    Individual structured recording inside a dataset.
    Categories: Speech, Singing, Rap, Harmony, Falsetto, Emotion, Scales, Sustained Notes.
    """
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
