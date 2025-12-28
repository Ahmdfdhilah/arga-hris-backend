from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING
from datetime import datetime as DateTimeType
from app.config.database import Base
from app.core.utils.datetime import get_utc_now

if TYPE_CHECKING:
    from app.modules.users.users.models.user import User
    from app.modules.users.rbac.models.role import Role
    from app.modules.employee_assignments.models.employee_assignment import (
        EmployeeAssignment,
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    created_at: Mapped[DateTimeType] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    # Temporary assignment support
    is_temporary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    valid_until: Mapped[Optional[DateTimeType]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assignment_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("employee_assignments.id", ondelete="SET NULL"),
        nullable=True,
    )

    user: Mapped["User"] = relationship("User", backref="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")
    assignment: Mapped[Optional["EmployeeAssignment"]] = relationship(
        "EmployeeAssignment", backref="temporary_roles"
    )

    def __repr__(self) -> str:
        temp_str = " (temporary)" if self.is_temporary else ""
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id}{temp_str})>"
