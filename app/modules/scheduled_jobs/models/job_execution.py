"""
Model untuk logging job execution history.
"""

from sqlalchemy import String, Integer, DateTime, Boolean, Text, Numeric
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, Any
from datetime import datetime as DateTimeType
from decimal import Decimal
from app.config.database import Base
from app.core.models.base_model import TimestampMixin


class JobExecution(Base, TimestampMixin):
    """
    Log history eksekusi scheduled jobs.
    
    Digunakan untuk monitoring, debugging, dan analytics.
    """

    __tablename__ = "job_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="Unique identifier job")
    
    started_at: Mapped[DateTimeType] = mapped_column(DateTime(timezone=True), nullable=False, comment="Waktu mulai eksekusi")
    finished_at: Mapped[Optional[DateTimeType]] = mapped_column(DateTime(timezone=True), nullable=True, comment="Waktu selesai eksekusi")
    duration_seconds: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3), nullable=True, comment="Durasi eksekusi dalam detik")
    
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Status keberhasilan eksekusi")
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Pesan hasil eksekusi")
    error_trace: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Stack trace jika error")
    
    result_data: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True, comment="Data hasil eksekusi (JSON)")

    def __repr__(self) -> str:
        return f"<JobExecution(id={self.id}, job_id={self.job_id}, success={self.success})>"
