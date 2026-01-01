"""
OrgUnit Model - Organization Unit master data

Represents organizational structure with hierarchical relationships.
This is the master data, owned by HRIS.
"""

import uuid
from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.employees.models.employee import Employee


class OrgUnit(Base, TimestampMixin):
    """Organization Unit model with hierarchical structure"""

    __tablename__ = "org_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("org_units.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    path: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    head_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey(
            "employees.id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_org_units_head_id",
        ),
        nullable=True,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, index=True
    )

    # Audit fields for soft delete - Native UUID
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    deleted_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    # Relationships
    parent: Mapped[Optional["OrgUnit"]] = relationship(
        "OrgUnit", remote_side=[id], back_populates="children", foreign_keys=[parent_id]
    )
    children: Mapped[List["OrgUnit"]] = relationship(
        "OrgUnit", back_populates="parent", foreign_keys=[parent_id]
    )
    head: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[head_id], back_populates="headed_units"
    )
    employees: Mapped[List["Employee"]] = relationship(
        "Employee", foreign_keys="Employee.org_unit_id", back_populates="org_unit"
    )

    # Indexes
    __table_args__ = (
        Index("ix_org_units_path_pattern", "path", postgresql_using="btree"),
    )

    def is_deleted(self) -> bool:
        """Check if org unit is soft deleted"""
        return self.deleted_at is not None

    def set_created_by(self, user_id: str) -> None:
        """Set created_by field"""
        self.created_by = user_id

    def set_updated_by(self, user_id: str) -> None:
        """Set updated_by field"""
        self.updated_by = user_id

    def set_deleted_by(self, user_id: str) -> None:
        """Set deleted_by field"""
        self.deleted_by = user_id

    def __repr__(self) -> str:
        return f"<OrgUnit(id={self.id}, code={self.code}, name={self.name})>"
