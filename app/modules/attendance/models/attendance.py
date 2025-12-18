from sqlalchemy import String, Integer, Date, DateTime, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import date as DateType, datetime as DateTimeType
from decimal import Decimal
from app.config.database import Base
from app.core.models.base_model import TimestampMixin


class Attendance(Base, TimestampMixin):
    """Attendance model for employee check-in/check-out records.

    Business constraints:
    - Work hours: 8 hours per day or 40 hours per week
    - Monday-Friday: 09:00 - 17:00 WIB
    - Saturday: 09:00 - 15:00 WIB
    - Photo for check-in and check-out are mandatory
    """

    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    org_unit_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True
    )
    attendance_date: Mapped[DateType] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="absent")

    # Core attendance data
    check_in_time: Mapped[Optional[DateTimeType]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    check_out_time: Mapped[Optional[DateTimeType]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    work_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Calculated work hours until 18:00 (e.g., 8.5 for 8 hours 30 minutes)",
    )
    overtime_hours: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Overtime hours after 18:00 (e.g., 2.5 for 2 hours 30 minutes)",
    )

    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Check-in specific fields
    check_in_submitted_at: Mapped[Optional[DateTimeType]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    check_in_submitted_ip: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    check_in_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    check_in_selfie_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="GCP storage path for check-in selfie (mandatory when check-in)",
    )
    check_in_latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 8), nullable=True, comment="Check-in latitude coordinate"
    )
    check_in_longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(11, 8), nullable=True, comment="Check-in longitude coordinate"
    )
    check_in_location_name: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Check-in location address from reverse geocoding",
    )

    # Check-out specific fields
    check_out_submitted_at: Mapped[Optional[DateTimeType]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    check_out_submitted_ip: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    check_out_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    check_out_selfie_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="GCP storage path for check-out selfie (mandatory when check-out)",
    )
    check_out_latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 8), nullable=True, comment="Check-out latitude coordinate"
    )
    check_out_longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(11, 8), nullable=True, comment="Check-out longitude coordinate"
    )
    check_out_location_name: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Check-out location address from reverse geocoding",
    )

    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, employee_id={self.employee_id}, date={self.attendance_date}, status={self.status})>"
