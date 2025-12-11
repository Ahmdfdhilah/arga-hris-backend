from sqlalchemy import String, Integer, Boolean, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List, TYPE_CHECKING
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.rbac.models.user_role import UserRole
    from app.modules.users.rbac.models.role_permission import RolePermission


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user_roles: Mapped[List["UserRole"]] = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    role_permissions: Mapped[List["RolePermission"]] = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"
