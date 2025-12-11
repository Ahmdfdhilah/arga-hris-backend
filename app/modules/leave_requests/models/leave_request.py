from sqlalchemy import String, Integer, Date, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import date as DateType
from app.config.database import Base
from app.core.models.base_model import TimestampMixin


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
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    leave_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    start_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    end_date: Mapped[DateType] = mapped_column(Date, nullable=False)
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "leave_type IN ('leave', 'holiday')",
            name="check_leave_type"
        ),
        CheckConstraint(
            "total_days > 0",
            name="check_total_days_positive"
        ),
    )

    def __repr__(self) -> str:
        return f"<LeaveRequest(id={self.id}, employee_id={self.employee_id}, leave_type={self.leave_type}, start_date={self.start_date}, end_date={self.end_date})>"
