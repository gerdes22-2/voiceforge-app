import os

with open("backend/app/services/storage_service.py", "w") as f:
    f.write("""import os
import shutil
import uuid
import hashlib
from typing import Tuple, Optional
from app.core.config import settings

class StorageService:
    def __init__(self, provider="local", base_path="/app/storage"):
        self.provider = provider
        self.base_path = base_path
        if self.provider == "local":
            os.makedirs(self.base_path, exist_ok=True)

    async def save_file(self, file_obj, original_filename: str) -> Tuple[str, str, int, str]:
        \"\"\"
        Saves a file, returning (storage_path, mime_type, size, sha256)
        \"\"\"
        file_ext = os.path.splitext(original_filename)[1].lower()
        new_filename = f"{uuid.uuid4()}{file_ext}"
        
        if self.provider == "local":
            file_path = os.path.join(self.base_path, new_filename)
            sha256_hash = hashlib.sha256()
            size = 0
            
            with open(file_path, "wb") as f_out:
                while chunk := await file_obj.read(1024 * 1024): # 1MB chunks
                    size += len(chunk)
                    sha256_hash.update(chunk)
                    f_out.write(chunk)
                    
            mime_type = "application/octet-stream"
            if file_ext == ".mp3": mime_type = "audio/mpeg"
            elif file_ext == ".wav": mime_type = "audio/wav"
            elif file_ext == ".flac": mime_type = "audio/flac"
            elif file_ext in [".m4a", ".aac"]: mime_type = "audio/aac"
            
            return file_path, mime_type, size, sha256_hash.hexdigest()
        else:
            raise NotImplementedError(f"Storage provider {self.provider} not implemented")
            
storage_service = StorageService()
""")

with open("backend/app/services/audio_metadata_service.py", "w") as f:
    f.write("""import os
from typing import Dict, Any

class AudioMetadataService:
    @staticmethod
    def extract_metadata(file_path: str) -> Dict[str, Any]:
        \"\"\"
        Extracts metadata using librosa/mutagen/ffprobe.
        For now, this is a mock implementation that returns plausible data.
        \"\"\"
        # TODO: Implement real extraction logic
        return {
            "duration_sec": 185.5,
            "sample_rate": 44100,
            "channels": 2,
            "bit_depth": 16,
            "bpm": 120.0,
            "musical_key": "C Minor",
            "loudness_lufs": -14.0,
            "peak_level_db": -1.0
        }
""")

with open("backend/app/schemas/upload.py", "w") as f:
    f.write("""from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class FileAssetRead(BaseModel):
    id: UUID
    file_name: str
    storage_provider: str
    mime_type: str
    size_bytes: int
    duration_sec: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    virus_scan_status: str

    class Config:
        from_attributes = True
        
class SongRead(BaseModel):
    id: UUID
    project_id: UUID
    title: Optional[str] = None
    status: str
    bpm: Optional[float] = None
    musical_key: Optional[str] = None
    loudness_lufs: Optional[float] = None
    
    class Config:
        from_attributes = True
""")

with open("backend/app/api/v1/uploads.py", "w") as f:
    f.write("""from typing import Any
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
    \"\"\"
    Upload a song file to a project.
    \"\"\"
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
""")
