"""
Core Messaging Module - RabbitMQ Integration
"""

from app.core.messaging.rabbitmq import RabbitMQManager, rabbitmq_manager
from app.core.messaging.event_publisher import EventPublisher
from app.core.messaging.events import DomainEvent, EventType

__all__ = [
    "RabbitMQManager",
    "rabbitmq_manager",
    "EventPublisher",
    "DomainEvent",
    "EventType",
]
