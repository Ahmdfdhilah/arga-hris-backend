"""
Response schemas untuk OrgUnit operations
"""

from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime


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
    number: str
    name: str
    position: Optional[str] = None

    class Config:
        from_attributes = True


class OrgUnitResponse(BaseModel):
    """Org unit response - field names match model exactly"""
    id: int
    code: str
    name: str
    type: str
    parent_id: Optional[int] = None
    head_id: Optional[int] = None
    level: int
    path: str
    description: Optional[str] = None
    metadata_: Optional[Dict[str, str]] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None
    # Nested relationships
    parent: Optional[OrgUnitParentNestedResponse] = None
    head: Optional[OrgUnitHeadNestedResponse] = None

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int
    limit: int
    total_items: int
    total_pages: int = 0


class OrgUnitListResponse(BaseModel):
    """Response for list of org units with pagination"""
    org_units: List[OrgUnitResponse]
    pagination: PaginationInfo


class OrgUnitHierarchyItem(BaseModel):
    """Recursive hierarchy item"""
    org_unit: OrgUnitResponse
    children: List['OrgUnitHierarchyItem'] = []


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
