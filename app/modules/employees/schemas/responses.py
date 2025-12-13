"""
Response schemas untuk Employee operations

Employee response now includes nested User for profile data.
"""

from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime


class EmployeeOrgUnitNestedResponse(BaseModel):
    """Nested org unit data in employee response"""
    id: int
    code: str
    name: str
    type: str

    class Config:
        from_attributes = True


class EmployeeSupervisorNestedResponse(BaseModel):
    """Nested supervisor data in employee response"""
    id: int
    number: str
    position: Optional[str] = None
    # User profile data
    user: Optional["UserNestedResponse"] = None

    class Config:
        from_attributes = True


class UserNestedResponse(BaseModel):
    """User profile data (synced from SSO)"""
    id: int
    sso_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    avatar_path: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    """
    Employee response - employment data with nested user profile.
    
    Profile data (name, email, phone, gender) comes from nested 'user'.
    Employment data (number, position, type, org_unit) is on employee.
    """
    id: int
    user_id: Optional[int] = None
    number: str
    position: Optional[str] = None
    type: Optional[str] = None  # on_site, hybrid, ho
    org_unit_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    metadata_: Optional[Dict[str, str]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    
    # Nested relationships
    user: Optional[UserNestedResponse] = None
    org_unit: Optional[EmployeeOrgUnitNestedResponse] = None
    supervisor: Optional[EmployeeSupervisorNestedResponse] = None

    class Config:
        from_attributes = True


# Update forward references
EmployeeSupervisorNestedResponse.model_rebuild()


class EmployeeAccountData(BaseModel):
    """Employee account data (Employee + temporary password)"""
    employee: EmployeeResponse
    temporary_password: Optional[str] = None
    warnings: Optional[List[str]] = None

    class Config:
        from_attributes = True


class EmployeeAccountUpdateData(BaseModel):
    """Response data untuk update employee with account"""
    employee: Optional[EmployeeResponse] = None
    updated_fields: Optional[Dict[str, bool]] = None
    warnings: Optional[List[str]] = None

    class Config:
        from_attributes = True


class EmployeeAccountListItem(BaseModel):
    """Single item in employee account list"""
    id: int
    sso_id: Optional[str] = None
    employee_id: Optional[int] = None
    name: str = ""
    email: str = ""
    is_active: bool = True

    class Config:
        from_attributes = True


class BulkInsertResult(BaseModel):
    """Result dari bulk insert operation"""
    total_items: int
    success_count: int
    error_count: int
    errors: List[dict] = []
    warnings: List[str] = []
    created_ids: List[int] = []

    class Config:
        from_attributes = True
