"""
User Model - Minimal linking table for SSO integration

Only stores:
- sso_id: Link to SSO user (UUID string)
- employee_id: Link to workforce employee
- org_unit_id: Cached from employee for quick lookup
- is_active: Local active status for HRIS
"""

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.config.database import Base
from app.core.models.base_model import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sso_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)  # UUID from SSO
    employee_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    org_unit_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, sso_id={self.sso_id}, employee_id={self.employee_id})>"
