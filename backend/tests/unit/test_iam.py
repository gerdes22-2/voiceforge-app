import pytest
from uuid7 import uuid7
from datetime import datetime, timezone, timedelta
from app.models.iam import Organization, OrganizationMember, RefreshToken, RolePermission
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import get_password_hash, verify_password

def test_password_hashing():
    password = "supersecretpassword123!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_organization_model():
    org = Organization(name="Test Studio", billing_email="billing@test.com")
    assert org.name == "Test Studio"

def test_organization_member():
    u_id = uuid7()
    o_id = uuid7()
    member = OrganizationMember(organization_id=o_id, user_id=u_id, role=UserRole.ARTIST)
    assert member.role == UserRole.ARTIST

def test_refresh_token_model():
    u_id = uuid7()
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    token = RefreshToken(user_id=u_id, token="random_token_string", expires_at=expires)
    assert token.token == "random_token_string"
    assert token.revoked_at is None
