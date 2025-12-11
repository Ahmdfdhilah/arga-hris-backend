"""Auth response schemas."""

from pydantic import BaseModel
from typing import Optional, List


class CurrentUserResponse(BaseModel):
    """Response schema untuk current user info."""

    id: int
    sso_id: Optional[int] = None
    email: str
    first_name: str
    last_name: str
    full_name: str
    employee_id: Optional[int] = None
    roles: List[str] = []
    permissions: List[str] = []
    is_active: bool = True

    class Config:
        from_attributes = True


class TokenInfoResponse(BaseModel):
    """Response schema untuk token info."""

    user_id: Optional[str] = None
    jti: Optional[str] = None
    exp: Optional[int] = None
    is_blacklisted: bool = False

    class Config:
        from_attributes = True


class TokenValidateResponse(BaseModel):
    """Response schema untuk token validation."""

    valid: bool

    class Config:
        from_attributes = True


class BlacklistStatsResponse(BaseModel):
    """Response schema untuk blacklist statistics."""

    blacklisted_tokens: int
    revoked_users: int

    class Config:
        from_attributes = True


class RefreshCacheResponse(BaseModel):
    """Response schema untuk refresh cache."""

    user_id: int
    refreshed: bool
    note: Optional[str] = None

    class Config:
        from_attributes = True
