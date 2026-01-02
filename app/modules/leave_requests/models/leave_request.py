import uuid
from sqlalchemy import String, Integer, Date, Text, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import date as DateType
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.employees.models.employee import Employee
    from app.modules.employee_assignments.models.employee_assignment import (
        EmployeeAssignment,
    )


class LeaveRequest(Base, TimestampMixin):
    """LeaveRequest model untuk permintaan cuti karyawan.

    Business constraints:
    - Employee hanya bisa melihat leave request miliknya sendiri
    - HR Admin/Super Admin dapat melakukan CRUD untuk semua leave request
    - Leave type: leave (cuti), holiday (libur)
    - Total days dihitung otomatis berdasarkan start_date dan end_date
    """

    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    start_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    end_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Replacement/Acting - optional fields untuk penggantian sementara
    replacement_employee_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assignment_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("employee_assignments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        foreign_keys=[employee_id],
        lazy="joined",
    )
    replacement_employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        foreign_keys=[replacement_employee_id],
        backref="leave_requests_as_replacement",
    )
    assignment: Mapped[Optional["EmployeeAssignment"]] = relationship(
        "EmployeeAssignment",
        foreign_keys=[assignment_id],
        backref="source_leave_request",
    )

    __table_args__ = (
        CheckConstraint("leave_type IN ('leave', 'holiday')", name="check_leave_type"),
        CheckConstraint("total_days > 0", name="check_total_days_positive"),
    )

    def __repr__(self) -> str:
        return f"<LeaveRequest(id={self.id}, employee_id={self.employee_id}, leave_type={self.leave_type}, start_date={self.start_date}, end_date={self.end_date})>"
