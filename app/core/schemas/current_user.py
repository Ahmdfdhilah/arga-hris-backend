"""Current user schema for dependency injection."""

from pydantic import BaseModel
from typing import Optional, List


class CurrentUser(BaseModel):
    """Schema for authenticated user data from JWT token."""

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
