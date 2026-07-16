import os

with open("backend/app/api/v1/voice_models.py", "w") as f:
    f.write("""from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.voice import VoiceModel
from pydantic import BaseModel
from app.models.user import User

class VoiceModelStatusUpdate(BaseModel):
    status: str # 'approved', 'rejected'

class VoiceModelRead(BaseModel):
    id: UUID
    name: str
    status: str
    training_metrics: dict | None
    
    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/{model_id}/status", response_model=VoiceModelRead)
async def update_model_status(
    model_id: UUID,
    status_update: VoiceModelStatusUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    \"\"\"
    Approval gate for Voice Models. Once training and evaluation are complete,
    a user can approve or reject the model to make it available for Voice Conversion.
    \"\"\"
    model = await db.get(VoiceModel, model_id)
    if not model or model.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Model not found")
        
    if status_update.status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    model.status = status_update.status
    await db.commit()
    await db.refresh(model)
    return model

@router.get("/{model_id}", response_model=VoiceModelRead)
async def get_model(
    model_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    model = await db.get(VoiceModel, model_id)
    if not model or model.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Model not found")
    return model
""")

with open("backend/app/api/v1/api.py", "a") as f:
    f.write("from app.api.v1 import voice_models\n")
    f.write("api_router.include_router(voice_models.router, prefix='/voice-models', tags=['voice-models'])\n")
