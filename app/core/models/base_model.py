from sqlalchemy import Column, DateTime
from app.core.utils.datetime import get_utc_now


class TimestampMixin:
    """
    Mixin class to add created_at and updated_at timestamp fields to models.

    Uses timezone-aware UTC datetime from app.core.utils.datetime.get_utc_now()
    instead of deprecated datetime.utcnow.

    Usage:
        class YourModel(Base, TimestampMixin):
            __tablename__ = "your_table"
            id = Column(Integer, primary_key=True)
            ...
    """

    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)
