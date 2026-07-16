from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.api import deps
from app.models.feedback import ConversionFeedback
from app.models.user import User

class FeedbackCreate(BaseModel):
    voice_model_id: UUID
    rating: int
    conversion_settings: dict
    song_type: str = "unknown"

router = APIRouter()

@router.post("/")
async def submit_feedback(
    feedback_in: FeedbackCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    feedback = ConversionFeedback(
        user_id=current_user.id,
        voice_model_id=feedback_in.voice_model_id,
        rating=feedback_in.rating,
        conversion_settings=feedback_in.conversion_settings,
        song_type=feedback_in.song_type
    )
    db.add(feedback)
    await db.commit()
    return {"status": "success"}
