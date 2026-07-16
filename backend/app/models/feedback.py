from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime
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
