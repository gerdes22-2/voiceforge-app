from uuid import UUID
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
