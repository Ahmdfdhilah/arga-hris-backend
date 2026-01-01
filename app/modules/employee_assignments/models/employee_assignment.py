"""
EmployeeAssignment Model - Temporary replacement during leave

Represents temporary employee assignments when someone takes leave.
Link ke leave request untuk tracking.
"""

import uuid
from sqlalchemy import String, Integer, Date, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import date as DateType
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.employees.models.employee import Employee
    from app.modules.org_units.models.org_unit import OrgUnit
    from app.modules.leave_requests.models.leave_request import LeaveRequest


class EmployeeAssignment(Base, TimestampMixin):
    """Track penggantian sementara employee untuk leave request"""

    __tablename__ = "employee_assignments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Siapa yang menggantikan dan yang digantikan
    employee_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    replaced_employee_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Organizational context
    org_unit_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("org_units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Period - always has start and end for leave context
    start_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    end_date: Mapped[DateType] = mapped_column(Date, nullable=False)

    # Status lifecycle
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )

    # Link to leave request (required)
    leave_request_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leave_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Metadata
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee", foreign_keys=[employee_id], backref="assignments_as_replacement"
    )
    replaced_employee: Mapped["Employee"] = relationship(
        "Employee", foreign_keys=[replaced_employee_id], backref="assignments_replaced"
    )
    org_unit: Mapped["OrgUnit"] = relationship("OrgUnit", backref="assignments")
    leave_request: Mapped["LeaveRequest"] = relationship(
        "LeaveRequest",
        foreign_keys=[leave_request_id],
        backref="linked_assignment",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'active', 'expired', 'cancelled')",
            name="ck_employee_assignments_status",
        ),
        CheckConstraint(
            "end_date >= start_date",
            name="ck_employee_assignments_date_range",
        ),
        CheckConstraint(
            "employee_id != replaced_employee_id",
            name="ck_employee_assignments_different_employees",
        ),
        Index(
            "ix_employee_assignments_status_dates",
            "status",
            "start_date",
            "end_date",
        ),
    )

    def __repr__(self) -> str:
        return f"<EmployeeAssignment(id={self.id}, employee_id={self.employee_id}, replaced={self.replaced_employee_id}, status={self.status})>"
