"""
Event Publisher

Publishes domain events to RabbitMQ with proper serialization,
routing, and delivery guarantees.
"""

import logging
from typing import Any, Dict, Optional

import aio_pika
from aio_pika import Message, DeliveryMode

from app.core.messaging.rabbitmq import RabbitMQManager, rabbitmq_manager
from app.core.messaging.events import DomainEvent, EventType

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    Publishes domain events to RabbitMQ.
    
    Features:
    - Persistent message delivery
    - Automatic serialization
    - Retry on failure
    - Correlation ID tracking
    """
    
    def __init__(self, manager: Optional[RabbitMQManager] = None):
        self._manager = manager or rabbitmq_manager
    
    async def publish(self, event: DomainEvent) -> bool:
        """
        Publish a domain event to RabbitMQ.
        
        Args:
            event: The domain event to publish
            
        Returns:
            True if published successfully, False otherwise
        """
        try:
            exchange = await self._manager.get_exchange()
            
            message = Message(
                body=event.to_json().encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
                correlation_id=event.correlation_id,
                headers={
                    "event_type": event.event_type.value,
                    "entity_type": event.entity_type,
                    "entity_id": str(event.entity_id),
                    "source": event.source,
                    "version": event.version,
                },
            )
            
            await exchange.publish(
                message,
                routing_key=event.routing_key,
            )
            
            logger.info(
                f"Published event: {event.routing_key} "
                f"(entity_id={event.entity_id}, correlation_id={event.correlation_id})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.routing_key}: {e}")
            return False
    
    async def publish_entity_event(
        self,
        event_type: EventType,
        entity_type: str,
        entity_id: int,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> bool:
        """
        Convenience method to publish an entity event.
        
        Args:
            event_type: Type of event (created, updated, deleted)
            entity_type: Type of entity (employee, org_unit)
            entity_id: ID of the entity
            data: Entity data to include in event
            correlation_id: Optional correlation ID for tracing
            
        Returns:
            True if published successfully
        """
        event = DomainEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            correlation_id=correlation_id,
        )
        return await self.publish(event)
    
    async def publish_employee_created(self, employee_id: int, data: Dict[str, Any]) -> bool:
        """Publish employee.created event"""
        return await self.publish_entity_event(
            EventType.CREATED, "employee", employee_id, data
        )
    
    async def publish_employee_updated(self, employee_id: int, data: Dict[str, Any]) -> bool:
        """Publish employee.updated event"""
        return await self.publish_entity_event(
            EventType.UPDATED, "employee", employee_id, data
        )
    
    async def publish_employee_deleted(self, employee_id: int, data: Dict[str, Any]) -> bool:
        """Publish employee.deleted event"""
        return await self.publish_entity_event(
            EventType.DELETED, "employee", employee_id, data
        )
    
    async def publish_org_unit_created(self, org_unit_id: int, data: Dict[str, Any]) -> bool:
        """Publish org_unit.created event"""
        return await self.publish_entity_event(
            EventType.CREATED, "org_unit", org_unit_id, data
        )
    
    async def publish_org_unit_updated(self, org_unit_id: int, data: Dict[str, Any]) -> bool:
        """Publish org_unit.updated event"""
        return await self.publish_entity_event(
            EventType.UPDATED, "org_unit", org_unit_id, data
        )
    
    async def publish_org_unit_deleted(self, org_unit_id: int, data: Dict[str, Any]) -> bool:
        """Publish org_unit.deleted event"""
        return await self.publish_entity_event(
            EventType.DELETED, "org_unit", org_unit_id, data
        )


# Global singleton instance
event_publisher = EventPublisher()
