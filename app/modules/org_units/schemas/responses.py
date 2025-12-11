from pydantic import BaseModel
from typing import Optional, Dict, List


class OrgUnitParentNestedResponse(BaseModel):
    """Nested parent org unit data in org unit response"""
    id: int
    code: str
    name: str
    type: str

    class Config:
        from_attributes = True


class OrgUnitHeadNestedResponse(BaseModel):
    """Nested head employee data in org unit response"""
    id: int
    employee_number: str
    name: str
    position: Optional[str] = None

    class Config:
        from_attributes = True


class OrgUnitResponse(BaseModel):
    """Org unit response matching gRPC contract from workforce service"""
    id: int
    code: str
    name: str
    type: str
    parent_id: Optional[int] = None
    head_id: Optional[int] = None
    level: int
    path: str
    description: Optional[str] = None
    org_unit_metadata: Optional[Dict[str, str]] = None
    is_active: bool = True
    employee_count: int = 0
    total_employee_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    parent: Optional[OrgUnitParentNestedResponse] = None
    head: Optional[OrgUnitHeadNestedResponse] = None
    deleted_at: Optional[str] = None
    deleted_by: Optional[int] = None

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    limit: int
    total_items: int
    total_pages: int


class OrgUnitListResponse(BaseModel):
    """Response for list of org units with pagination"""
    org_units: List[OrgUnitResponse]
    pagination: PaginationInfo


class OrgUnitHierarchyItem(BaseModel):
    """Recursive hierarchy item"""
    org_unit: OrgUnitResponse
    children: List['OrgUnitHierarchyItem'] = []


# For forward reference support
OrgUnitHierarchyItem.model_rebuild()


class OrgUnitHierarchyResponse(BaseModel):
    """Organization unit hierarchy response"""
    root: Optional[OrgUnitResponse] = None
    hierarchy: List[OrgUnitHierarchyItem] = []


class OrgUnitTypesResponse(BaseModel):
    """Response for org unit types"""
    types: List[str]


class OrgUnitDeleteResult(BaseModel):
    """Result from delete operation"""
    success: bool
    message: str


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
