from typing import Optional, List, Dict, Any
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
