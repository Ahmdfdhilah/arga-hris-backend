"""
Event Consumer Infrastructure

Provides standardized event handling across all services.
"""

from app.core.messaging.consumer.base import BaseEventHandler, DomainEvent
from app.core.messaging.consumer.registry import EventHandlerRegistry, handles
from app.core.messaging.consumer.consumer import EventConsumer

__all__ = [
    "BaseEventHandler",
    "DomainEvent",
    "EventHandlerRegistry",
    "handles",
    "EventConsumer",
]
