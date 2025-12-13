"""
Messaging Dependencies

FastAPI dependency injection for event publisher.
"""

from typing import Annotated
from fastapi import Depends

from app.core.messaging.event_publisher import EventPublisher, event_publisher


def get_event_publisher() -> EventPublisher:
    """Get the global event publisher instance"""
    return event_publisher


EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]
