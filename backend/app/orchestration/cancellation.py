from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workflow import Workflow, WorkflowTask, TaskState
from app.orchestration.engine import WorkflowEngine
from app.orchestration.lifecycle import LifecycleManager

class CancellationManager:
    @staticmethod
    async def cancel_workflow(db: AsyncSession, workflow_id: UUID) -> bool:
        """
        Gracefully terminates a workflow.
        Signals external workers to stop processing (mocked here).
        """
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
