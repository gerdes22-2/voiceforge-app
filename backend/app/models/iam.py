from typing import Optional, List
import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, UUIDMixin, TimestampMixin, SoftDeleteMixin
from .enums import UserRole

class Organization(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organizations"
    """Root entity for workspaces"""
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    billing_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    members: Mapped[List["OrganizationMember"]] = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="organization", cascade="all, delete-orphan")

class OrganizationMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organization_members"
    """Link between User and Organization with a specific role"""
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.GUEST, nullable=False)
    
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="organization_memberships")

class RefreshToken(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "refresh_tokens"
    """Stores refresh tokens for token rotation and session management"""
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    replaced_by_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")

class RolePermission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "role_permissions"
    """Defines what actions each role can perform"""
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    resource: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 'project', 'voice_model'
    action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. 'create', 'delete', 'train'
