"""
gRPC Utility Functions for HRIS Backend

Shared helpers for gRPC handlers.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from google.protobuf.timestamp_pb2 import Timestamp


def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[Timestamp]:
    """Convert datetime to protobuf Timestamp."""
    if dt is None:
        return None
    timestamp = Timestamp()
    timestamp.FromDatetime(dt)
    return timestamp


def metadata_to_dict(metadata) -> Dict[str, str]:
    """Convert protobuf map to Python dict."""
    if metadata is None:
        return {}
    return dict(metadata)
