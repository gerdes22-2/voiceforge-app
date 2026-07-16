import os

os.makedirs("backend/app/orchestration", exist_ok=True)
os.makedirs("backend/app/models", exist_ok=True)

# 1. Models update
with open("backend/app/models/workflow.py", "w") as f:
    f.write("""from typing import Optional, List
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
    \"\"\"
    Represents an overarching DAG execution.
    \"\"\"
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TaskState] = mapped_column(Enum(TaskState), default=TaskState.PENDING, nullable=False)
    target_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("file_assets.id", ondelete="SET NULL"), nullable=True) # e.g. target song to process
    
    tasks: Mapped[List["WorkflowTask"]] = relationship("WorkflowTask", back_populates="workflow", cascade="all, delete-orphan")

class WorkflowTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_tasks"
    \"\"\"
    A specific step/node in the workflow DAG.
    \"\"\"
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
""")

# Append to __init__.py safely
with open("backend/app/models/__init__.py", "a") as f:
    f.write("from .workflow import Workflow, WorkflowTask, TaskState\n")

# 2. DAG Engine
with open("backend/app/orchestration/engine.py", "w") as f:
    f.write("""from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workflow import Workflow, WorkflowTask, TaskState

class WorkflowEngine:
    \"\"\"
    Evaluates the DAG and determines which tasks are ready to run.
    \"\"\"
    @staticmethod
    async def get_runnable_tasks(db: AsyncSession, workflow_id: UUID) -> List[WorkflowTask]:
        \"\"\"
        Returns tasks that have all dependencies met (COMPLETED) and are in PENDING state.
        \"\"\"
        query = select(WorkflowTask).where(WorkflowTask.workflow_id == workflow_id)
        result = await db.execute(query)
        tasks = list(result.scalars().all())
        
        task_dict = {str(t.id): t for t in tasks}
        runnable = []
        
        for t in tasks:
            if t.status in (TaskState.PENDING, TaskState.RETRYING):
                # Check dependencies
                deps_met = True
                for dep_id in t.depends_on:
                    dep_task = task_dict.get(dep_id)
                    if not dep_task or dep_task.status != TaskState.COMPLETED:
                        deps_met = False
                        break
                
                if deps_met:
                    runnable.append(t)
                    
        return runnable

    @staticmethod
    async def mark_cancelled(db: AsyncSession, workflow_id: UUID):
        \"\"\"
        Cascade cancellation to all non-terminal tasks in a workflow.
        \"\"\"
        query = select(WorkflowTask).where(WorkflowTask.workflow_id == workflow_id)
        result = await db.execute(query)
        tasks = list(result.scalars().all())
        
        for t in tasks:
            if t.status not in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
                t.status = TaskState.CANCELLED
        
        workflow = await db.get(Workflow, workflow_id)
        if workflow:
            workflow.status = TaskState.CANCELLED
            
        await db.commit()
""")

# 3. Cache Manager
with open("backend/app/orchestration/cache.py", "w") as f:
    f.write("""import hashlib
import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.models.audio import AudioCache

class CacheManager:
    \"\"\"
    Generates deterministic hashes for inputs/parameters to reuse previous processing results.
    \"\"\"
    @staticmethod
    def generate_hash(task_type: str, input_params: Dict[str, Any]) -> str:
        # Sort keys to ensure consistent hashing
        param_str = json.dumps(input_params, sort_keys=True)
        raw_key = f"{task_type}:{param_str}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    async def get_cached_result(db: AsyncSession, hash_key: str) -> Optional[AudioCache]:
        query = select(AudioCache).where(
            AudioCache.hash_key == hash_key
        )
        result = await db.execute(query)
        cache_entry = result.scalar_one_or_none()
        
        if cache_entry:
            # Check expiry
            if cache_entry.expires_at and cache_entry.expires_at < datetime.now(timezone.utc):
                return None
            return cache_entry
            
        return None

    @staticmethod
    async def store_cache_result(db: AsyncSession, task_type: str, input_params: Dict[str, Any], output_urls: Dict[str, str], expires_at: Optional[datetime] = None):
        hash_key = CacheManager.generate_hash(task_type, input_params)
        
        # In a real scenario, we might store multiple outputs (e.g. vocals, instrumental)
        # We can store them as JSON in a single Cache record, or individual records.
        # For AudioCache model as currently defined, it expects a single file_url.
        # We can adapt to store the main file or serialized dict.
        
        cache_entry = AudioCache(
            hash_key=hash_key,
            artifact_type=task_type,
            file_url=json.dumps(output_urls), # Storing dict as JSON string here for flexibility
            generation_params=input_params,
            expires_at=expires_at
        )
        db.add(cache_entry)
        await db.commit()
""")

# 4. Lifecycle & Scheduler
with open("backend/app/orchestration/lifecycle.py", "w") as f:
    f.write("""from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.workflow import WorkflowTask, TaskState
from app.crud.crud_timeline import timeline as crud_timeline

class LifecycleManager:
    @staticmethod
    async def transition_state(db: AsyncSession, task: WorkflowTask, new_state: TaskState, project_id: UUID, message: str = ""):
        old_state = task.status
        task.status = new_state
        
        if new_state == TaskState.RUNNING and not task.started_at:
            task.started_at = datetime.now(timezone.utc)
        elif new_state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
            task.completed_at = datetime.now(timezone.utc)
            
        if message:
            task.error_message = message if new_state == TaskState.FAILED else None
            
        await db.commit()
        
        # Log to project timeline
        await crud_timeline.create(
            db=db,
            project_id=project_id,
            event_type=f"task_{new_state.value}",
            description=f"Task {task.task_type} transitioned from {old_state.value} to {new_state.value}. {message}"
        )
""")

# 5. Retry Manager
with open("backend/app/orchestration/retry.py", "w") as f:
    f.write("""from app.models.workflow import WorkflowTask, TaskState
from sqlalchemy.ext.asyncio import AsyncSession

class RetryManager:
    @staticmethod
    async def handle_failure(db: AsyncSession, task: WorkflowTask) -> TaskState:
        \"\"\"
        Decides if a task should be retried or marked as permanently failed.
        \"\"\"
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskState.RETRYING
            # Apply backoff logic here if scheduling immediately vs delayed
        else:
            task.status = TaskState.FAILED
            
        await db.commit()
        return task.status
""")

