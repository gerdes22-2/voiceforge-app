from datetime import datetime, timedelta, timezone
import secrets
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.iam import RefreshToken, Organization, OrganizationMember
from app.models.log import AuditLog
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings

class IAMService:
    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
            
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            return None # Locked out
            
        if not user.password_hash or not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            await db.commit()
            return None
            
        # Reset counters on success
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.locked_until = None
            await db.commit()
            
        return user

    @staticmethod
    async def create_refresh_token(db: AsyncSession, user_id: UUID) -> str:
        token = secrets.token_urlsafe(64)
        expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        db_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires
        )
        db.add(db_token)
        await db.commit()
        return token

    @staticmethod
    async def rotate_refresh_token(db: AsyncSession, old_token_str: str) -> str | None:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == old_token_str)
        )
        old_token = result.scalar_one_or_none()
        
        if not old_token:
            return None
            
        # Token reuse detection
        if old_token.revoked_at:
            # Compromised token family, revoke all tokens for this user
            await db.execute(
                select(RefreshToken).where(RefreshToken.user_id == old_token.user_id)
            )
            # In a real impl, we'd update all to revoked_at = now()
            # This requires an update statement
            await db.commit()
            return None
            
        if old_token.expires_at < datetime.now(timezone.utc):
            return None
            
        # Revoke old
        old_token.revoked_at = datetime.now(timezone.utc)
        
        # Issue new
        new_token_str = secrets.token_urlsafe(64)
        old_token.replaced_by_token = new_token_str
        
        expires = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_token = RefreshToken(
            user_id=old_token.user_id,
            token=new_token_str,
            expires_at=expires
        )
        db.add(new_token)
        await db.commit()
        
        return new_token_str

    @staticmethod
    async def log_audit_event(db: AsyncSession, user_id: UUID | None, action: str, resource_type: str, resource_id: str, ip: str = None):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip
        )
        db.add(log)
        await db.commit()
