
from enum import Enum

class EventType(str, Enum):
    """Standard event types"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RESTORED = "restored"