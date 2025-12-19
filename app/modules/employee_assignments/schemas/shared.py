"""
Shared schemas untuk Employee Assignments module.
"""

from enum import Enum


class AssignmentStatus(str, Enum):
    """Status lifecycle untuk employee assignment."""

    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

    @classmethod
    def values_string(cls) -> str:
        """Return comma-separated values untuk dokumentasi."""
        return ", ".join([s.value for s in cls])
