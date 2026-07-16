from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workflow import WorkflowTask, TaskState
from app.orchestration.lifecycle import LifecycleManager

class Scheduler:
    """
    The intelligent scheduler. 
    Decides CPU vs GPU, prioritizes jobs, assigns workers.
    """
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
        """
        Mock dispatcher.
        """
        print(f"Dispatching task {task_id} to {'GPU' if needs_gpu else 'CPU'} worker queue.")
