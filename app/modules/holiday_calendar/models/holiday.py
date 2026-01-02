"""
Holiday Model - Hari Libur Nasional dan Cuti Bersama

Menyimpan daftar hari libur nasional dan cuti bersama yang berlaku.
Digunakan oleh scheduled jobs untuk skip auto-create attendance.
"""

import uuid
from sqlalchemy import String, Integer, Date, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import date as DateType
from app.config.database import Base
from app.core.models.base_model import TimestampMixin


class Holiday(Base, TimestampMixin):
    """Model untuk menyimpan hari libur nasional dan cuti bersama.
    
    Attributes:
        date: Tanggal libur
        name: Nama hari libur (contoh: Hari Kemerdekaan RI)
        description: Deskripsi tambahan (opsional)
        is_active: Status aktif untuk soft toggle
    """

    __tablename__ = "holidays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[DateType] = mapped_column(Date, nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Audit fields
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Holiday(id={self.id}, date={self.date}, name={self.name})>"
