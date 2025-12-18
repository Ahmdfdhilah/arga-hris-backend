from sqlalchemy import (
    String,
    Integer,
    Date,
    Text,
    CheckConstraint,
    UniqueConstraint,
    DateTime
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, Any
from datetime import date as DateType, datetime as DateTimeType
from app.config.database import Base
from app.core.models.base_model import TimestampMixin


class WorkSubmission(Base, TimestampMixin):
    """WorkSubmission model untuk dokumentasi bulanan karyawan.

    Business constraints:
    - Employee hanya bisa melihat submission miliknya sendiri
    - HR Admin/Super Admin dapat melakukan CRUD untuk semua submissions
    - Satu employee hanya bisa memiliki 1 submission per bulan
    - Status: draft (bisa edit), submitted (final)
    - Files disimpan dalam JSONB array dengan metadata lengkap
    """

    __tablename__ = "work_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    submission_month: Mapped[DateType] = mapped_column(Date, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    files: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", index=True
    )
    submitted_at: Mapped[Optional[DateTimeType]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "employee_id", "submission_month", name="uq_employee_submission_month"
        ),
        CheckConstraint(
            "status IN ('draft', 'submitted')", name="check_submission_status_valid"
        ),
    )

    def __repr__(self) -> str:
        return f"<WorkSubmission(id={self.id}, employee_id={self.employee_id}, month={self.submission_month}, status={self.status})>"
