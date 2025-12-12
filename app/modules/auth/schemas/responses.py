"""Auth response schemas - updated for SSO integration."""

from pydantic import BaseModel
from typing import Optional, List


class CurrentUserResponse(BaseModel):
    """Response schema untuk current user info - combines SSO + HRIS data."""

    # HRIS local data
    id: int
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    
    # SSO data
    sso_id: str
    name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    sso_role: str = "user"
    
    # HRIS RBAC
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
    """Response schema untuk blacklist statistics (deprecated)."""

    blacklisted_tokens: int = 0
    revoked_users: int = 0

    class Config:
        from_attributes = True


class RefreshCacheResponse(BaseModel):
    """Response schema untuk refresh cache (deprecated)."""

    user_id: int
    refreshed: bool
    note: Optional[str] = None

    class Config:
        from_attributes = True
