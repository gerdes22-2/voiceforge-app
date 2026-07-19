from sqlalchemy import String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import Base, UUIDMixin, TimestampMixin
import uuid

class ConversionFeedback(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversion_feedbacks"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    voice_model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("voice_models.id"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    conversion_settings: Mapped[dict] = mapped_column(JSON, nullable=True)
    song_type: Mapped[str] = mapped_column(String, nullable=True)

