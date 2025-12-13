"""
Employee Model - Employee master data

Represents employee information with organizational relationships.
This is the master data, owned by HRIS.
"""

from sqlalchemy import String, Integer, Boolean, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.org_units.models.org_unit import OrgUnit


class Employee(Base, TimestampMixin):
    """Employee model with organizational relationships"""
    
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employee_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    employee_gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    org_unit_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("org_units.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    supervisor_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("employees.id", ondelete="SET NULL"), 
        nullable=True, 
        index=True
    )
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Audit fields for soft delete
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, index=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    org_unit: Mapped[Optional["OrgUnit"]] = relationship(
        "OrgUnit",
        foreign_keys=[org_unit_id],
        back_populates="employees"
    )
    supervisor: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        remote_side=[id],
        back_populates="subordinates",
        foreign_keys=[supervisor_id]
    )
    subordinates: Mapped[List["Employee"]] = relationship(
        "Employee",
        back_populates="supervisor",
        foreign_keys=[supervisor_id]
    )
    headed_units: Mapped[List["OrgUnit"]] = relationship(
        "OrgUnit",
        foreign_keys="OrgUnit.head_id",
        back_populates="head"
    )

    # Constraints and indexes
    __table_args__ = (
        CheckConstraint(
            "employee_type IN ('on_site', 'hybrid', 'ho') OR employee_type IS NULL",
            name="ck_employees_employee_type"
        ),
        CheckConstraint(
            "employee_gender IN ('male', 'female') OR employee_gender IS NULL",
            name="ck_employees_employee_gender"
        ),
        Index('ix_employees_name_search', 'name', postgresql_using='btree'),
    )

    def is_deleted(self) -> bool:
        """Check if employee is soft deleted"""
        return self.deleted_at is not None

    def set_created_by(self, user_id: int) -> None:
        """Set created_by field"""
        self.created_by = user_id

    def set_updated_by(self, user_id: int) -> None:
        """Set updated_by field"""
        self.updated_by = user_id

    def set_deleted_by(self, user_id: int) -> None:
        """Set deleted_by field"""
        self.deleted_by = user_id

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, number={self.number}, name={self.name})>"
