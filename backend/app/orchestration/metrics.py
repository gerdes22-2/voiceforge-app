from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.job import JobQueueMetric # Reuse existing metric model or create WorkflowMetric
from app.models.workflow import WorkflowTask

class MetricsCollector:
    @staticmethod
    async def record_task_metrics(db: AsyncSession, task: WorkflowTask):
        """
        Records detailed telemetry for optimization.
        """
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
