"""
Employee Model - Employment data

Represents employee employment information with organizational relationships.
Profile data (name, email, phone, gender) is stored in User table.
This table focuses on employment-specific data.
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
    from app.modules.users.users.models.user import User


class Employee(Base, TimestampMixin):
    """Employee model - employment data with user profile link"""
    
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Link to user profile (one-to-one)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True,
        index=True
    )
    
    # Employee identification
    number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Employment data
    position: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # on_site, hybrid, ho
    
    # Organization structure
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
    
    # Additional data
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Audit fields for soft delete
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True, index=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="employee",
        foreign_keys=[user_id]
    )
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

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "type IN ('on_site', 'hybrid', 'ho') OR type IS NULL",
            name="ck_employees_type"
        ),
        Index('ix_employees_number_search', 'number', postgresql_using='btree'),
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
        return f"<Employee(id={self.id}, number={self.number})>"
