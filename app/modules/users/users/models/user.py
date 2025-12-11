from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.guests.models.guest_account import GuestAccount


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sso_id: Mapped[Optional[int]] = mapped_column(Integer, unique=True, nullable=True, index=True)
    employee_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    org_unit_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), default='regular', nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    employee_deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    guest_account: Mapped[Optional["GuestAccount"]] = relationship("GuestAccount", back_populates="user", uselist=False, foreign_keys="[GuestAccount.user_id]")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, sso_id={self.sso_id})>"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
