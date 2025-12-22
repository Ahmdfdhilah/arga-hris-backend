"""
Employee Response Schemas
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserNestedResponse(BaseModel):
    """User profile data (synced from SSO)"""

    id: str  # SSO UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    avatar_path: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class EmployeeOrgUnitNestedResponse(BaseModel):
    """Nested org unit"""

    id: int
    code: str
    name: str
    type: str

    class Config:
        from_attributes = True


class EmployeeSupervisorNestedResponse(BaseModel):
    """Nested supervisor"""

    id: int
    code: str
    name: Optional[str] = None
    position: Optional[str] = None
    user: Optional[UserNestedResponse] = None

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    """Employee with nested user profile"""

    id: int
    user_id: Optional[str] = None
    code: str
    name: Optional[str] = None  # Denormalized from user
    email: Optional[str] = None  # Denormalized from user
    position: Optional[str] = None
    site: Optional[str] = None  # on_site, hybrid, ho
    type: Optional[str] = None  # fulltime, contract, intern
    org_unit_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    user: Optional[UserNestedResponse] = None
    org_unit: Optional[EmployeeOrgUnitNestedResponse] = None
    supervisor: Optional[EmployeeSupervisorNestedResponse] = None

    class Config:
        from_attributes = True


EmployeeSupervisorNestedResponse.model_rebuild()


class BulkInsertResult(BaseModel):
    """Bulk insert result"""

    total_items: int
    success_count: int
    error_count: int
    errors: List[dict] = []
    warnings: List[str] = []
    created_ids: List[int] = []
