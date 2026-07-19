from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db, get_current_user
from app.models import User, Project, Song
from app.schemas.song import SongRead
from app.services.storage import storage_service
import uuid
import logging

logger = logging.getLogger("backend.songs")
router = APIRouter()

ALLOWED_MIME_TYPES = ["audio/mpeg", "audio/wav", "audio/flac", "audio/mp4", "audio/aac"]

@router.post("", response_model=SongRead, status_code=status.HTTP_201_CREATED)
async def upload_song(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 1. Verify Project belongs to User
    query = select(Project).where(
        Project.id == project_id,
        Project.user_id == current_user.id,
        Project.deleted_at.is_(None)
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # 2. Validate File Type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
        
    # 3. Save to Storage
    file_uuid = uuid.uuid4()
    extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
    destination_path = f"projects/{project_id}/songs/{file_uuid}.{extension}"
    
    try:
        remote_path = await storage_service.upload(file.file, destination_path, file.content_type)
        logger.info(f"File uploaded to storage: {remote_path}")
    except Exception as e:
        logger.error(f"Storage upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")
        
    # 4. Save to Database
    song = Song(
        project_id=project.id,
        original_file_uuid=file_uuid,
        status="uploaded"
    )
    db.add(song)
    await db.commit()
    await db.refresh(song)
    
    logger.info(f"Song record created: {song.id}")
    return song
