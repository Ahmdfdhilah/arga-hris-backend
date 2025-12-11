from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, TYPE_CHECKING
from datetime import datetime as DateTimeType
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.users.users.models.user import User


class GuestAccount(Base, TimestampMixin):
    __tablename__ = "guest_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), unique=True, nullable=False, index=True)
    guest_type: Mapped[str] = mapped_column(String(50), nullable=False)
    valid_from: Mapped[DateTimeType] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[DateTimeType] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    sponsor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="guest_account", foreign_keys=[user_id])
    sponsor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[sponsor_id])

    def __repr__(self) -> str:
        return f"<GuestAccount(id={self.id}, user_id={self.user_id}, guest_type={self.guest_type})>"
