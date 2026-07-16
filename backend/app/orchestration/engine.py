from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.workflow import Workflow, WorkflowTask, TaskState

class WorkflowEngine:
    """
    Evaluates the DAG and determines which tasks are ready to run.
    """
    @staticmethod
    async def get_runnable_tasks(db: AsyncSession, workflow_id: UUID) -> List[WorkflowTask]:
        """
        Returns tasks that have all dependencies met (COMPLETED) and are in PENDING state.
        """
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
        """
        Cascade cancellation to all non-terminal tasks in a workflow.
        """
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
