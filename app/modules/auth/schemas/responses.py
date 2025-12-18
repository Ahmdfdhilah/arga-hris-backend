"""Auth response schemas - simplified for SSO integration."""

from pydantic import BaseModel
from typing import Optional, List


class CurrentUserResponse(BaseModel):
    """Response schema for current user info - combines SSO + HRIS data."""

    # User identity (SSO UUID)
    id: str  # SSO user UUID
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None

    # SSO profile data
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
