import os

with open("backend/app/schemas/workflow.py", "w") as f:
    f.write("""from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.workflow import TaskState

class WorkflowTaskRead(BaseModel):
    id: UUID
    workflow_id: UUID
    task_type: str
    status: TaskState
    depends_on: List[str]
    progress: float
    retry_count: int
    input_params: Optional[Dict[str, Any]] = None
    output_artifacts: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkflowRead(BaseModel):
    id: UUID
    project_id: UUID
    name: str
    status: TaskState
    target_asset_id: Optional[UUID] = None
    tasks: List[WorkflowTaskRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowCreate(BaseModel):
    project_id: UUID
    target_asset_id: UUID
    # In a real app, we might specify which predefined DAG to build
""")

with open("backend/app/api/v1/workflows.py", "w") as f:
    f.write("""from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api import deps
from app.schemas.workflow import WorkflowCreate, WorkflowRead
from app.models.workflow import Workflow, TaskState
from app.models.user import User
from app.orchestration.builder import WorkflowBuilder
from app.orchestration.engine import WorkflowEngine
from app.orchestration.scheduler import Scheduler
from app.orchestration.cancellation import CancellationManager
from app.orchestration.lifecycle import LifecycleManager

router = APIRouter()

@router.post("/", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    *,
    db: AsyncSession = Depends(deps.get_db),
    workflow_in: WorkflowCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Initiates a new Vocal Processing workflow.
    \"\"\"
    # TODO: check project permissions
    
    # 1. Build DAG
    workflow = await WorkflowBuilder.create_vocal_processing_workflow(
        db=db,
        project_id=workflow_in.project_id,
        target_asset_id=workflow_in.target_asset_id
    )
    
    # 2. Start initial tasks
    runnable = await WorkflowEngine.get_runnable_tasks(db, workflow.id)
    if runnable:
        await Scheduler.schedule_tasks(db, runnable)
        
    await db.refresh(workflow, ["tasks"])
    return workflow

@router.get("/{workflow_id}", response_model=WorkflowRead)
async def read_workflow(
    *,
    db: AsyncSession = Depends(deps.get_db),
    workflow_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    query = select(Workflow).options(selectinload(Workflow.tasks)).where(Workflow.id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    return workflow

@router.post("/{workflow_id}/cancel")
async def cancel_workflow(
    *,
    db: AsyncSession = Depends(deps.get_db),
    workflow_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Cancel an ongoing workflow gracefully.
    \"\"\"
    success = await CancellationManager.cancel_workflow(db, workflow_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel workflow. It might already be finished.")
    return {"status": "cancelled"}

@router.post("/{workflow_id}/resume")
async def resume_workflow(
    *,
    db: AsyncSession = Depends(deps.get_db),
    workflow_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Resume a workflow from its last successful state.
    Skips COMPLETED nodes, reschedules FAILED or CANCELLED nodes if parents are COMPLETED.
    \"\"\"
    query = select(Workflow).options(selectinload(Workflow.tasks)).where(Workflow.id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    # Reset FAILED or CANCELLED tasks to PENDING
    for task in workflow.tasks:
        if task.status in (TaskState.FAILED, TaskState.CANCELLED):
            task.status = TaskState.PENDING
            task.error_message = None
            
    workflow.status = TaskState.PENDING
    await db.commit()
    
    # Re-evaluate and schedule
    runnable = await WorkflowEngine.get_runnable_tasks(db, workflow.id)
    if runnable:
        await Scheduler.schedule_tasks(db, runnable)
        
    return {"status": "resumed"}
""")

with open("backend/app/api/v1/api.py", "a") as f:
    f.write("from app.api.v1 import workflows\n")
    f.write("api_router.include_router(workflows.router, prefix='/workflows', tags=['workflows'])\n")
