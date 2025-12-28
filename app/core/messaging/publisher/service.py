
import json
import logging
from typing import Any, Dict, Optional
from aio_pika import Message, DeliveryMode

from app.core.messaging.engine import message_engine
from app.core.messaging.types import DomainEvent

logger = logging.getLogger(__name__)

class EventPublisher:
    """
    Standard event publisher using MessageEngine.
    """
    
    def __init__(self, service_name: str = "hris"):
        self.service_name = service_name
        self.engine = message_engine

    async def publish(self, event: DomainEvent, exchange_name: str = "hris.events") -> bool:
        """
        Publish a domain event to the specified exchange.
        """
        try:
            channel = await self.engine.get_channel()
            exchange = await channel.get_exchange(exchange_name)
            
            # Ensure source service is set correctly
            event.source_service = self.service_name
            
            message = Message(
                body=json.dumps(event.to_dict()).encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
                correlation_id=event.correlation_id,
                headers={
                    "service": self.service_name,
                    "version": str(event.version)
                }
            )
            
            await exchange.publish(message, routing_key=event.get_routing_key())
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event.get_routing_key()}: {e}")
            return False

# Global Instance
event_publisher = EventPublisher()
