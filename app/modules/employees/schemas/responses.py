"""
Response schemas untuk Employee operations - Simplified (SSO-first)
"""

from pydantic import BaseModel
from typing import Optional, Dict, List


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
    employee_number: str
    name: str
    position: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    """Employee response matching gRPC contract from workforce service"""
    id: int
    employee_number: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    employee_type: Optional[str] = None
    employee_gender: Optional[str] = None
    org_unit_id: Optional[int] = None
    supervisor_id: Optional[int] = None
    employee_metadata: Optional[Dict[str, str]] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    org_unit: Optional[EmployeeOrgUnitNestedResponse] = None
    supervisor: Optional[EmployeeSupervisorNestedResponse] = None
    user_id: Optional[int] = None
    deleted_at: Optional[str] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class UserNestedResponse(BaseModel):
    """User data - HRIS user is minimal now (linking only)"""
    id: int
    sso_id: str
    employee_id: Optional[int] = None
    org_unit_id: Optional[int] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# Keep for backward compat but deprecated
class GuestAccountNestedResponse(BaseModel):
    """Deprecated - Guest handling is in SSO now"""
    id: int = 0
    user_id: int = 0
    guest_type: str = ""

    class Config:
        from_attributes = True


class EmployeeAccountData(BaseModel):
    """Employee account data (Employee + SSO User link)"""
    employee: EmployeeResponse
    user: Optional[UserNestedResponse] = None
    guest_account: Optional[GuestAccountNestedResponse] = None  # Always None now
    temporary_password: Optional[str] = None
    warnings: Optional[List[str]] = None

    class Config:
        from_attributes = True


class EmployeeAccountUpdateData(BaseModel):
    """Response data untuk update employee with account"""
    employee: Optional[EmployeeResponse] = None
    user: Optional[UserNestedResponse] = None
    guest_account: Optional[GuestAccountNestedResponse] = None  # Always None now
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
