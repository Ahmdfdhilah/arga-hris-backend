from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING
from datetime import datetime as DateTimeType
from app.config.database import Base
from app.core.utils.datetime import get_utc_now

if TYPE_CHECKING:
    from app.modules.users.users.models.user import User
    from app.modules.users.rbac.models.role import Role


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    created_at: Mapped[DateTimeType] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    user: Mapped["User"] = relationship("User", backref="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
