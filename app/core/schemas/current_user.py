"""Current user schema for dependency injection.

Combines data from:
- SSO (profile data via gRPC)
- HRIS DB (local user id, employee_id, HRIS-specific roles)
"""

from pydantic import BaseModel
from typing import Optional, List


class CurrentUser(BaseModel):
    """Schema for authenticated user data."""

    # HRIS local data
    id: int  # HRIS user ID
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    
    # SSO data
    sso_id: str  # UUID from SSO
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
