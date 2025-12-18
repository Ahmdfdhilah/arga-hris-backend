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
    number: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_employee(cls, employee) -> "OrgUnitHeadNestedResponse":
        """Create response from Employee model with user relationship."""
        name = None
        if employee.user:
            name = employee.user.name
        return cls(
            id=employee.id,
            number=employee.number,
            name=name,
            position=employee.position,
        )


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
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None
    # Nested relationships
    parent: Optional[OrgUnitParentNestedResponse] = None
    head: Optional[OrgUnitHeadNestedResponse] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_head(cls, org_unit) -> "OrgUnitResponse":
        """Create response from OrgUnit model with proper head name resolution."""
        data = {
            "id": org_unit.id,
            "code": org_unit.code,
            "name": org_unit.name,
            "type": org_unit.type,
            "parent_id": org_unit.parent_id,
            "head_id": org_unit.head_id,
            "level": org_unit.level,
            "path": org_unit.path,
            "description": org_unit.description,
            "metadata_": org_unit.metadata_,
            "is_active": org_unit.is_active,
            "created_at": org_unit.created_at,
            "updated_at": org_unit.updated_at,
            "created_by": org_unit.created_by,
            "updated_by": org_unit.updated_by,
            "deleted_at": org_unit.deleted_at,
            "deleted_by": org_unit.deleted_by,
        }

        # Build parent
        if org_unit.parent:
            data["parent"] = OrgUnitParentNestedResponse.model_validate(org_unit.parent)

        # Build head with user.name
        if org_unit.head:
            data["head"] = OrgUnitHeadNestedResponse.from_employee(org_unit.head)

        return cls(**data)


class OrgUnitHierarchyItem(BaseModel):
    """Recursive hierarchy item"""

    org_unit: OrgUnitResponse
    children: List["OrgUnitHierarchyItem"] = []


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
