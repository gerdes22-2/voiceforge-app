from app.models.workflow import WorkflowTask, TaskState
from sqlalchemy.ext.asyncio import AsyncSession

class RetryManager:
    @staticmethod
    async def handle_failure(db: AsyncSession, task: WorkflowTask) -> TaskState:
        """
        Decides if a task should be retried or marked as permanently failed.
        """
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            task.status = TaskState.RETRYING
            # Apply backoff logic here if scheduling immediately vs delayed
        else:
            task.status = TaskState.FAILED
            
        await db.commit()
        return task.status
