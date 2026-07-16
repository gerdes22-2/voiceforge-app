from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api import deps
from app.models.storage import FileAsset
from app.models.audio import Song
from app.models.user import User
from app.schemas.upload import FileAssetRead, SongRead
from app.services.storage_service import storage_service
from app.services.audio_metadata_service import AudioMetadataService
from app.crud.crud_timeline import timeline as crud_timeline

router = APIRouter()

ALLOWED_MIME_TYPES = ["audio/wav", "audio/mpeg", "audio/flac", "audio/aac", "audio/x-m4a"]
ALLOWED_EXTENSIONS = [".wav", ".mp3", ".flac", ".aac", ".m4a"]

@router.post("/song", response_model=SongRead, status_code=status.HTTP_201_CREATED)
async def upload_song(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: UUID = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a song file to a project.
    """
    # Validation
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format.")
        
    # 1. Save File
    file_path, mime_type, size, checksum = await storage_service.save_file(file, file.filename)
    
    # 2. Extract Metadata
    metadata = AudioMetadataService.extract_metadata(file_path)
    
    # 3. Create FileAsset
    file_asset = FileAsset(
        user_id=current_user.id,
        file_name=file.filename,
        storage_provider=storage_service.provider,
        storage_path=file_path,
        mime_type=mime_type,
        size_bytes=size,
        sha256_checksum=checksum,
        duration_sec=metadata.get("duration_sec"),
        sample_rate=metadata.get("sample_rate"),
        channels=metadata.get("channels"),
        bit_depth=metadata.get("bit_depth")
    )
    db.add(file_asset)
    await db.flush() # get file_asset.id
    
    # 4. Create Song
    song = Song(
        project_id=project_id,
        file_asset_id=file_asset.id,
        title=file.filename,
        status="metadata_extracted",
        bpm=metadata.get("bpm"),
        musical_key=metadata.get("musical_key"),
        loudness_lufs=metadata.get("loudness_lufs"),
        peak_level_db=metadata.get("peak_level_db")
    )
    db.add(song)
    await db.commit()
    await db.refresh(song)
    
    # 5. Update Timeline
    await crud_timeline.create(
        db=db,
        project_id=project_id,
        event_type="song_uploaded",
        description=f"Song '{file.filename}' was uploaded and analyzed."
    )
    
    return song
