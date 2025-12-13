"""
User Model - Profile replica from SSO

Stores user profile data synced from SSO Master:
- sso_id: Link to SSO user (UUID string)
- Profile fields: name, email, phone, gender, avatar_path (from SSO)
- synced_at: Last sync timestamp
- is_active: Local active status

Employee relationship links employment data to user profile.
"""

from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.config.database import Base
from app.core.models.base_model import TimestampMixin

if TYPE_CHECKING:
    from app.modules.employees.models.employee import Employee


class User(Base, TimestampMixin):
    """User profile - replica from SSO"""
    
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sso_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    
    # Profile data (synced from SSO)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # male, female
    avatar_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Sync metadata
    synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        server_default=func.now()
    )
    
    # Local state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationship to Employee (one-to-one)
    employee: Mapped[Optional["Employee"]] = relationship(
        "Employee",
        back_populates="user",
        uselist=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, sso_id={self.sso_id}, name={self.name})>"
