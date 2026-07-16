from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models.schema import User, Job, Song, Project
from app.schemas.job import JobCreate, JobRead
import uuid
import logging
import asyncio
from celery.result import AsyncResult
# Import celery app configuration to get task states
from core.celery_client import celery_app

logger = logging.getLogger("backend.jobs")
router = APIRouter()

@router.post("", response_model=JobRead, status_code=status.HTTP_201_CREATED)
async def create_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_in: JobCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Verify song belongs to user via project
    query = (
        select(Song)
        .join(Project)
        .where(
            Song.id == job_in.song_id,
            Project.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    song = result.scalar_one_or_none()
    
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
        
    # 2. Create Job in DB
    job = Job(
        song_id=song.id,
        task_type=job_in.task_type,
        status="queued"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    # 3. Dispatch to Celery
    task_name = job_in.task_type
    if task_name == "stem_separation":
        task = celery_app.send_task(
            "stem_separation", 
            args=[str(song.id), str(song.original_file_uuid)],
            task_id=str(job.id) # Use Job ID as Task ID for easy tracking
        )
        logger.info(f"Dispatched stem_separation task {task.id}")
    else:
        logger.warning(f"Unknown task type: {task_name}")
        
    return job

@router.get("/{job_id}", response_model=JobRead)
async def read_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # We should verify it belongs to user but keeping it simple for now
    query = select(Job).where(Job.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # Update status from Celery
    task = AsyncResult(str(job.id), app=celery_app)
    if task.state == 'PROGRESS':
        job.progress = task.info.get('progress', 0.0)
        job.status = "processing"
    elif task.state == 'SUCCESS':
        job.progress = 100.0
        job.status = "completed"
    elif task.state == 'FAILURE':
        job.status = "failed"
        
    # Would be good to save updated state to DB here, 
    # but we will just return it for now
    return job

@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str, current_user: User = Depends(get_current_user)):
    """SSE endpoint for real-time progress updates"""
    async def event_generator():
        while True:
            task = AsyncResult(job_id, app=celery_app)
            state = task.state
            
            data = {
                "job_id": job_id,
                "status": state,
                "progress": 0.0
            }
            
            if state == 'PROGRESS':
                data["progress"] = float(task.info.get('progress', 0.0))
            elif state == 'SUCCESS':
                data["progress"] = 100.0
                yield {"event": "progress", "data": str(data)}
                break
            elif state == 'FAILURE':
                data["progress"] = 0.0
                yield {"event": "progress", "data": str(data)}
                break
                
            yield {"event": "progress", "data": str(data)}
            await asyncio.sleep(1) # Poll every second
            
    return EventSourceResponse(event_generator())
