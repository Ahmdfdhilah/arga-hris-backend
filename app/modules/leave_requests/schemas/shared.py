"""
Shared schemas untuk leave_requests module.
Schemas yang digunakan bersama antara requests dan responses.
"""
from enum import Enum


class LeaveType(str, Enum):
    """
    Enum untuk jenis cuti/libur.
    Digunakan di LeaveRequestCreateRequest, LeaveRequestUpdateRequest, dan LeaveRequestResponse.
    """
    LEAVE = "leave"
    HOLIDAY = "holiday"

    @classmethod
    def values(cls):
        """Return list of valid leave type values"""
        return [leave_type.value for leave_type in cls]

    @classmethod
    def values_string(cls):
        """Return comma-separated string of valid leave type values"""
        return ", ".join(cls.values())
