import os

os.makedirs("backend/app/orchestration", exist_ok=True)

# 6. Cancellation Manager
with open("backend/app/orchestration/cancellation.py", "w") as f:
    f.write("""from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workflow import Workflow, WorkflowTask, TaskState
from app.orchestration.engine import WorkflowEngine
from app.orchestration.lifecycle import LifecycleManager

class CancellationManager:
    @staticmethod
    async def cancel_workflow(db: AsyncSession, workflow_id: UUID) -> bool:
        \"\"\"
        Gracefully terminates a workflow.
        Signals external workers to stop processing (mocked here).
        \"\"\"
        workflow = await db.get(Workflow, workflow_id)
        if not workflow or workflow.status in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
            return False
            
        # Broadcast cancellation signal to workers (e.g. via Redis/Celery)
        # TODO: Implement worker signal broker
        
        # Mark all pending/running tasks as cancelled
        await WorkflowEngine.mark_cancelled(db, workflow_id)
        
        # Emit timeline event
        await LifecycleManager.transition_state(
            db, 
            workflow, 
            TaskState.CANCELLED, 
            workflow.project_id, 
            "Workflow cancelled by user."
        )
        return True
""")

# 7. Scheduler
with open("backend/app/orchestration/scheduler.py", "w") as f:
    f.write("""from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import WorkflowTask, TaskState
from app.orchestration.lifecycle import LifecycleManager

class Scheduler:
    \"\"\"
    The intelligent scheduler. 
    Decides CPU vs GPU, prioritizes jobs, assigns workers.
    \"\"\"
    @staticmethod
    async def schedule_tasks(db: AsyncSession, tasks: List[WorkflowTask]):
        for task in tasks:
            # Analyze task type to determine resource needs
            # E.g., 'stem_separation' -> GPU, 'metadata_extraction' -> CPU
            needs_gpu = task.task_type in ['stem_separation', 'voice_conversion', 'voice_training']
            
            # Here we would check available workers. For now, we mock queuing it.
            await LifecycleManager.transition_state(db, task, TaskState.QUEUED, task.workflow.project_id)
            
            # Trigger celery/rq/kafka worker
            Scheduler.dispatch_to_worker(task.id, needs_gpu)
            
    @staticmethod
    def dispatch_to_worker(task_id, needs_gpu: bool):
        \"\"\"
        Mock dispatcher.
        \"\"\"
        print(f"Dispatching task {task_id} to {'GPU' if needs_gpu else 'CPU'} worker queue.")
""")

# 8. Artifact Manager
with open("backend/app/orchestration/artifact.py", "w") as f:
    f.write("""from typing import Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.storage import FileAsset
from app.services.storage_service import storage_service

class ArtifactManager:
    \"\"\"
    Handles intermediate DAG outputs and registers them as reusable FileAssets.
    \"\"\"
    @staticmethod
    async def register_artifact(db: AsyncSession, user_id: UUID, file_path: str, original_name: str) -> FileAsset:
        \"\"\"
        Wraps a generated file into a standard FileAsset.
        \"\"\"
        # Note: In a real system, the worker uploads the artifact and provides metadata.
        # Here we mock the registration using the existing storage structures.
        
        # We would compute size/sha256 here if not provided by worker
        file_asset = FileAsset(
            user_id=user_id,
            file_name=original_name,
            storage_provider=storage_service.provider,
            storage_path=file_path,
            mime_type="application/octet-stream", # Should be derived
            size_bytes=0, # Mock
            is_validated=True
        )
        db.add(file_asset)
        await db.commit()
        await db.refresh(file_asset)
        return file_asset
""")

# 9. Metrics Collection
with open("backend/app/orchestration/metrics.py", "w") as f:
    f.write("""from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import JobQueueMetric # Reuse existing metric model or create WorkflowMetric
from app.models.workflow import WorkflowTask

class MetricsCollector:
    @staticmethod
    async def record_task_metrics(db: AsyncSession, task: WorkflowTask):
        \"\"\"
        Records detailed telemetry for optimization.
        \"\"\"
        if not task.started_at or not task.completed_at:
            return
            
        duration = (task.completed_at - task.started_at).total_seconds()
        
        # Assuming JobQueueMetric is used for tracking worker performance
        metric = JobQueueMetric(
            timestamp=datetime.now(timezone.utc),
            queue_name=task.task_type,
            active_jobs=1, # Mock
            pending_jobs=0, # Mock
            failed_jobs=1 if task.status == 'failed' else 0,
            avg_wait_time_sec=0.0 # Could calculate from created_at to started_at
        )
        db.add(metric)
        await db.commit()
""")

# 10. Workflow Builder (DAG definition)
with open("backend/app/orchestration/builder.py", "w") as f:
    f.write("""from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import Workflow, WorkflowTask, TaskState

class WorkflowBuilder:
    \"\"\"
    Constructs the DAG dynamically.
    \"\"\"
    @staticmethod
    async def create_vocal_processing_workflow(db: AsyncSession, project_id: UUID, target_asset_id: UUID) -> Workflow:
        \"\"\"
        Upload -> Metadata -> Stem Separation -> (Transcribe & Pitch) -> Conversion -> Master
        \"\"\"
        workflow = Workflow(
            project_id=project_id,
            name="Full Vocal Processing",
            status=TaskState.PENDING,
            target_asset_id=target_asset_id
        )
        db.add(workflow)
        await db.flush() # get ID
        
        # Node 1: Metadata
        metadata = WorkflowTask(
            workflow_id=workflow.id,
            task_type="metadata_extraction",
            depends_on=[],
            input_params={"asset_id": str(target_asset_id)}
        )
        db.add(metadata)
        await db.flush()
        
        # Node 2: Stem Separation
        stem_sep = WorkflowTask(
            workflow_id=workflow.id,
            task_type="stem_separation",
            depends_on=[str(metadata.id)],
            input_params={"model": "htdemucs"}
        )
        db.add(stem_sep)
        await db.flush()
        
        # Node 3a: Transcribe
        transcribe = WorkflowTask(
            workflow_id=workflow.id,
            task_type="transcription",
            depends_on=[str(stem_sep.id)],
            input_params={"model": "whisper-v3"}
        )
        db.add(transcribe)
        
        # Node 3b: Pitch Detection
        pitch = WorkflowTask(
            workflow_id=workflow.id,
            task_type="pitch_detection",
            depends_on=[str(stem_sep.id)],
            input_params={"algorithm": "rmvpe"}
        )
        db.add(pitch)
        await db.flush()
        
        # Node 4: Voice Conversion
        conversion = WorkflowTask(
            workflow_id=workflow.id,
            task_type="voice_conversion",
            depends_on=[str(transcribe.id), str(pitch.id)],
            input_params={"f0_method": "rmvpe"}
        )
        db.add(conversion)
        await db.flush()
        
        await db.commit()
        return workflow
""")

