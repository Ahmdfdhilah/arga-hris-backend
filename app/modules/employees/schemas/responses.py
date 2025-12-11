from pydantic import BaseModel, EmailStr
from typing import Optional, Dict,  List


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
    """User data in employee account response"""
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    org_unit_id: Optional[int] = None
    employee_id: Optional[int] = None
    account_type: str = 'regular'
    is_active: bool = True
    sso_id: Optional[int] = None

    class Config:
        from_attributes = True


class GuestAccountNestedResponse(BaseModel):
    """Guest account data in employee account response"""
    id: int
    user_id: int
    guest_type: str
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None
    sponsor_id: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeAccountData(BaseModel):
    """Unified employee account data (Employee + User + Guest)"""
    employee: EmployeeResponse
    user: Optional[UserNestedResponse] = None
    guest_account: Optional[GuestAccountNestedResponse] = None
    temporary_password: Optional[str] = None
    warnings: List[str] = []

    class Config:
        from_attributes = True


class EmployeeAccountUpdateData(BaseModel):
    """Response data untuk update employee with account"""
    employee: Optional[EmployeeResponse] = None
    user: UserNestedResponse
    guest_account: Optional[GuestAccountNestedResponse] = None
    updated_fields: Dict[str, List[str]]
    warnings: List[str] = []

    class Config:
        from_attributes = True


class EmployeeAccountListItem(BaseModel):
    """Single item in employee account list"""
    employee: Optional[EmployeeResponse] = None
    user: UserNestedResponse
    guest_account: Optional[GuestAccountNestedResponse] = None

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
