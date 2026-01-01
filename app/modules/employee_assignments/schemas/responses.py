import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.modules.employee_assignments.schemas.shared import AssignmentStatus


class EmployeeNestedResponse(BaseModel):
    """Employee ringkas untuk nested response"""

    id: int
    code: str
    name: Optional[str] = None
    position: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_employee(cls, employee) -> "EmployeeNestedResponse":
        """Create dari Employee model dengan user relationship."""
        name = employee.name  # Use denormalized name first
        if not name and employee and hasattr(employee, "user") and employee.user:
            name = employee.user.name
        return cls(
            id=employee.id,
            code=employee.code,
            name=name,
            position=employee.position,
        )


class OrgUnitNestedResponse(BaseModel):
    """Org unit ringkas untuk nested response"""

    id: int
    code: str
    name: str
    type: str

    class Config:
        from_attributes = True


class LeaveRequestNestedResponse(BaseModel):
    """Leave request ringkas untuk nested response"""

    id: int
    leave_type: str
    start_date: date
    end_date: date
    total_days: int

    class Config:
        from_attributes = True


class AssignmentResponse(BaseModel):
    """Full assignment response dengan nested relationships"""

    id: int
    employee_id: int
    replaced_employee_id: int
    org_unit_id: int
    start_date: date
    end_date: date
    status: AssignmentStatus
    leave_request_id: int
    reason: Optional[str] = None
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Nested relationships
    employee: Optional[EmployeeNestedResponse] = None
    replaced_employee: Optional[EmployeeNestedResponse] = None
    org_unit: Optional[OrgUnitNestedResponse] = None
    leave_request: Optional[LeaveRequestNestedResponse] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_relationships(cls, assignment) -> "AssignmentResponse":
        """Create response dengan proper relationship handling."""
        data = {
            "id": assignment.id,
            "employee_id": assignment.employee_id,
            "replaced_employee_id": assignment.replaced_employee_id,
            "org_unit_id": assignment.org_unit_id,
            "start_date": assignment.start_date,
            "end_date": assignment.end_date,
            "status": assignment.status,
            "leave_request_id": assignment.leave_request_id,
            "reason": assignment.reason,
            "created_by": assignment.created_by,
            "updated_by": assignment.updated_by,
            "created_at": assignment.created_at,
            "updated_at": assignment.updated_at,
        }

        # Build nested employee
        if assignment.employee:
            data["employee"] = EmployeeNestedResponse.from_employee(assignment.employee)

        # Build nested replaced employee
        if assignment.replaced_employee:
            data["replaced_employee"] = EmployeeNestedResponse.from_employee(
                assignment.replaced_employee
            )

        # Build nested org unit
        if assignment.org_unit:
            data["org_unit"] = OrgUnitNestedResponse.model_validate(assignment.org_unit)

        # Build nested leave request
        if assignment.leave_request:
            data["leave_request"] = LeaveRequestNestedResponse.model_validate(
                assignment.leave_request
            )

        return cls(**data)


class AssignmentListItemResponse(BaseModel):
    """Assignment ringkas untuk list view"""

    id: int
    employee_name: Optional[str] = None
    replaced_employee_name: Optional[str] = None
    org_unit_name: Optional[str] = None
    start_date: date
    end_date: date
    status: AssignmentStatus

    class Config:
        from_attributes = True

    @classmethod
    def from_assignment(cls, assignment) -> "AssignmentListItemResponse":
        """Create list item response."""
        employee_name = None
        replaced_employee_name = None
        org_unit_name = None

        if assignment.employee and assignment.employee.user:
            employee_name = assignment.employee.user.name

        if assignment.replaced_employee and assignment.replaced_employee.user:
            replaced_employee_name = assignment.replaced_employee.user.name

        if assignment.org_unit:
            org_unit_name = assignment.org_unit.name

        return cls(
            id=assignment.id,
            employee_name=employee_name,
            replaced_employee_name=replaced_employee_name,
            org_unit_name=org_unit_name,
            start_date=assignment.start_date,
            end_date=assignment.end_date,
            status=assignment.status,
        )
