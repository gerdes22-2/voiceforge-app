from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.system import ModelRegistry
from app.models.workflow import WorkflowTask

class ModelTracker:
    """
    Records EXACTLY which model version, commit, and parameters were used for an execution.
    """
    @staticmethod
    async def record_execution(
        db: AsyncSession, 
        task: WorkflowTask, 
        model_name: str, 
        version: str, 
        commit_hash: str, 
        inference_params: Dict[str, Any]
    ):
        # Attach telemetry to the task or a dedicated execution log
        if not task.metadata_info:
            task.metadata_info = {}
            
        task.metadata_info["model_execution"] = {
            "name": model_name,
            "version": version,
            "commit_hash": commit_hash,
            "inference_params": inference_params
        }
        await db.commit()
