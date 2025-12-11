from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING
from datetime import datetime as DateTimeType
from app.config.database import Base
from app.core.utils.datetime import get_utc_now

if TYPE_CHECKING:
    from app.modules.users.rbac.models.role import Role
    from app.modules.users.rbac.models.permission import Permission


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    created_at: Mapped[DateTimeType] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    role: Mapped["Role"] = relationship("Role", back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship("Permission", back_populates="role_permissions")

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
