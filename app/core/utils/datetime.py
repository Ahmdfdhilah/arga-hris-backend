from datetime import datetime, timezone
from typing import Optional


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp())


def from_timestamp(ts: int) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(fmt)


def parse_datetime(date_string: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    return datetime.strptime(date_string, fmt).replace(tzinfo=timezone.utc)


def is_past(dt: datetime) -> bool:
    return dt < utcnow()


def is_future(dt: datetime) -> bool:
    return dt > utcnow()


def get_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format with timezone"""
    return datetime.now(timezone.utc).isoformat()


def get_utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)
