from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List, TYPE_CHECKING
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.rbac.models.role_permission import RolePermission


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resource: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    role_permissions: Mapped[List["RolePermission"]] = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code={self.code})>"
