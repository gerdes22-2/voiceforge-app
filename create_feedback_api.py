import os

with open("backend/app/models/feedback.py", "w") as f:
    f.write("""from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base
import uuid

class ConversionFeedback(Base):
    __tablename__ = "conversion_feedbacks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    voice_model_id = Column(UUID(as_uuid=True), ForeignKey("voice_models.id"))
    rating = Column(Integer, nullable=False)
    conversion_settings = Column(JSON)
    song_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""")

with open("backend/app/models/__init__.py", "a") as f:
    f.write("from app.models.feedback import ConversionFeedback\n")

os.makedirs("backend/app/api/v1", exist_ok=True)
with open("backend/app/api/v1/feedbacks.py", "w") as f:
    f.write("""from fastapi import APIRouter, Depends, HTTPException
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
""")

# Edit backend/app/api/v1/api.py to include feedbacks router
import re
with open("backend/app/api/v1/api.py", "r") as f:
    content = f.read()

if "from app.api.v1 import feedbacks" not in content:
    content = content.replace(
        "from app.api.v1 import users", 
        "from app.api.v1 import users, feedbacks"
    )
    content += "api_router.include_router(feedbacks.router, prefix='/feedbacks', tags=['feedbacks'])\n"
    with open("backend/app/api/v1/api.py", "w") as f:
        f.write(content)

