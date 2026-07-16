from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class VoiceDatasetItemBase(BaseModel):
    category: str
    emotion_tag: Optional[str] = None
    quality_score: Optional[float] = None

class VoiceDatasetItemCreate(VoiceDatasetItemBase):
    file_asset_id: UUID

class VoiceDatasetItemRead(VoiceDatasetItemBase):
    id: UUID
    dataset_id: UUID
    file_asset_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class VoiceDatasetBase(BaseModel):
    name: str
    description: Optional[str] = None

class VoiceDatasetCreate(VoiceDatasetBase):
    pass

class VoiceDatasetRead(VoiceDatasetBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    items: List[VoiceDatasetItemRead] = []

    class Config:
        from_attributes = True
