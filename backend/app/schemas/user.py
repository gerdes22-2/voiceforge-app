from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    profile_data: Optional[dict] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str
    role: UserRole = UserRole.ARTIST

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserRead(UserBase):
    id: UUID
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
