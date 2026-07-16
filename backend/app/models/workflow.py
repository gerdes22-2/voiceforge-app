from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Float, Integer, Enum, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
import enum

class TaskState(str, enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    WAITING_FOR_GPU = "waiting_for_gpu"
    RUNNING = "running"
    PAUSED = "paused"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Workflow(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "workflows"
    """
    Represents an overarching DAG execution.
    """
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TaskState] = mapped_column(Enum(TaskState), default=TaskState.PENDING, nullable=False)
    target_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("file_assets.id", ondelete="SET NULL"), nullable=True) # e.g. target song to process
    
    tasks: Mapped[List["WorkflowTask"]] = relationship("WorkflowTask", back_populates="workflow", cascade="all, delete-orphan")

class WorkflowTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_tasks"
    """
    A specific step/node in the workflow DAG.
    """
    workflow_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False) # e.g., 'stem_separation', 'pitch_detection'
    status: Mapped[TaskState] = mapped_column(Enum(TaskState), default=TaskState.PENDING, nullable=False)
    
    # DAG Definition
    depends_on: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False) # List of parent Task IDs
    
    # Execution info
    worker_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # I/O
    input_params: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    output_artifacts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Telemetry
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="tasks")
