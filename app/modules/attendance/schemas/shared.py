"""
Shared schemas untuk attendance module.
Schemas yang digunakan bersama antara requests dan responses.
"""
from enum import Enum


class AttendanceStatus(str, Enum):
    """
    Enum untuk status kehadiran.
    Digunakan di AttendanceCreateRequest, AttendanceUpdateRequest, dan AttendanceResponse.
    """
    PRESENT = "present"
    ABSENT = "absent"
    LEAVE = "leave"
    HYBRID = "hybrid"
    INVALID = "invalid"
    
    @classmethod
    def values(cls):
        """Return list of valid status values"""
        return [status.value for status in cls]
    
    @classmethod
    def values_string(cls):
        """Return comma-separated string of valid status values"""
        return ", ".join(cls.values())
