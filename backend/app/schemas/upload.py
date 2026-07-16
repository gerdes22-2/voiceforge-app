from typing import Optional
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
