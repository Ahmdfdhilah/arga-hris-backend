from datetime import datetime, timezone, date, timedelta
from typing import  Tuple


def get_date_range_from_type(period_type: str) -> Tuple[date, date]:
    """
    Get start and end date based on period type (today/weekly/monthly).
    Raises ValueError if type is unknown.
    """
    today = date.today()
    if period_type == "today":
        return (today, today)
    elif period_type == "weekly":
        # Assuming start of week is Monday
        start_of_week = today - timedelta(days=today.weekday())
        return (start_of_week, today)
    elif period_type == "monthly":
        start_of_month = today.replace(day=1)
        return (start_of_month, today)
    else:
        raise ValueError(f"Unknown period type: {period_type}")


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
