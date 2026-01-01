"""Current user schema for dependency injection.

Combines data from:
- SSO (profile data via JWT)
- HRIS DB (employee_id, HRIS-specific roles)
"""

import uuid
from pydantic import BaseModel
from typing import Optional, List


class CurrentUser(BaseModel):
    """Schema for authenticated user data."""

    # User identity (SSO UUID)
    id: uuid.UUID  # SSO user UUID
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None

    # SSO profile data
    name: str  # Full name from SSO
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    sso_role: str = "user"  # Role in SSO

    # HRIS RBAC
    roles: List[str] = []  # HRIS roles
    permissions: List[str] = []  # HRIS permissions

    is_active: bool = True

    class Config:
        from_attributes = True
