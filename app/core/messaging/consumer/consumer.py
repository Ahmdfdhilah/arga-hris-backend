"""
Event Consumer - Main consumer loop for RabbitMQ messages

Connects to RabbitMQ and dispatches events to registered handlers.
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable, Any

from aio_pika import IncomingMessage
from aio_pika.abc import AbstractIncomingMessage

from app.core.messaging.rabbitmq import RabbitMQManager
from app.core.messaging.consumer.base import DomainEvent
from app.core.messaging.consumer.registry import EventHandlerRegistry

logger = logging.getLogger(__name__)


class EventConsumer:
    """
    Main event consumer - connects to RabbitMQ and dispatches to handlers.
    
    Features:
    - Automatic message acknowledgment after successful handling
    - Dead-letter queue for failed messages
    - Skips events from own service (idempotency)
    - Configurable prefetch for load balancing
    
    Usage:
        consumer = EventConsumer(rabbitmq_manager, "hris")
        await consumer.start("hris.events")
    """
    
    def __init__(
        self,
        rabbitmq: RabbitMQManager,
        service_name: str,
        db_session_factory: Optional[Callable] = None,
    ):
        """
        Initialize consumer.
        
        Args:
            rabbitmq: RabbitMQ connection manager
            service_name: Name of this service (for skip-own-events)
            db_session_factory: Optional factory for DB sessions in handlers
        """
        self.rabbitmq = rabbitmq
        self.service_name = service_name
        self.db_session_factory = db_session_factory
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(
        self,
        queue_name: str,
        prefetch_count: int = 10,
    ) -> None:
        """
        Start consuming messages from queue.
        
        Args:
            queue_name: Queue to consume from
            prefetch_count: Max unacknowledged messages per consumer
        """
        if self._running:
            logger.warning("Consumer already running")
            return
        
        try:
            channel = await self.rabbitmq.get_channel()
            await channel.set_qos(prefetch_count=prefetch_count)
            
            queue = await channel.get_queue(queue_name)
            
            logger.info(
                f"Consumer started | queue={queue_name} | "
                f"prefetch={prefetch_count} | service={self.service_name}"
            )
            
            # Log registered handlers
            all_handlers = EventHandlerRegistry.list_all()
            for event_type, handlers in all_handlers.items():
                logger.info(f"  {event_type} → {', '.join(handlers)}")
            
            self._running = True
            
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if not self._running:
                        break
                    await self._process_message(message)
                    
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
            self._running = False
            raise
    
    def start_background(self, queue_name: str, prefetch_count: int = 10) -> asyncio.Task:
        """
        Start consumer as background task.
        
        Returns:
            asyncio.Task that can be cancelled
        """
        self._task = asyncio.create_task(
            self.start(queue_name, prefetch_count)
        )
        return self._task
    
    async def stop(self) -> None:
        """Stop consumer gracefully."""
        if not self._running:
            return
        
        logger.info("Consumer stopping...")
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Consumer stopped")
    
    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        """
        Process a single message.
        
        Flow:
        1. Parse message to DomainEvent
        2. Skip if from own service
        3. Find handlers
        4. Execute handlers
        5. Ack/Nack based on result
        """
        async with message.process(requeue=False):
            try:
                # Parse message
                event = self._parse_message(message)
                if not event:
                    return  # Invalid message, already logged
                
                # Skip own events (idempotency protection)
                if event.source_service == self.service_name:
                    logger.debug(
                        f"Skipping own event: {event.get_routing_key()} "
                        f"from {event.source_service}"
                    )
                    return
                
                # Find handlers
                handlers = EventHandlerRegistry.get_handlers(event.get_routing_key())
                if not handlers:
                    logger.warning(f"No handler registered for: {event.get_routing_key()}")
                    return
                
                # Execute handlers
                for handler_class in handlers:
                    await self._execute_handler(handler_class, event)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in message: {e}")
            except Exception as e:
                logger.error(f"Message processing failed: {e}", exc_info=True)
                # Message will go to dead-letter if configured
                raise
    
    def _parse_message(self, message: AbstractIncomingMessage) -> Optional[DomainEvent]:
        """Parse RabbitMQ message to DomainEvent."""
        try:
            body = json.loads(message.body.decode())
            
            # Parse timestamp
            timestamp_str = body.get("timestamp")
            if timestamp_str:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                timestamp = datetime.utcnow()
            
            return DomainEvent(
                entity_type=body.get("entity_type", ""),
                event_action=body.get("event_type", ""),  # Publisher sends action as "event_type"
                entity_id=body.get("entity_id"),
                data=body.get("data", {}),
                timestamp=timestamp,
                source_service=body.get("source", body.get("source_service", "unknown")),
                correlation_id=body.get("correlation_id", ""),
                version=body.get("version", 1),
            )
        except Exception as e:
            logger.error(f"Failed to parse message: {e}")
            return None
    
    async def _execute_handler(
        self,
        handler_class: type,
        event: DomainEvent,
    ) -> None:
        """Execute a single handler."""
        handler = handler_class()
        
        try:
            # Check if handler wants to process this event
            if not await handler.can_handle(event):
                logger.debug(
                    f"{handler_class.__name__} skipped {event.get_routing_key()}"
                )
                return
            
            # Execute handler
            await handler.handle(event)
            await handler.on_success(event)
            
        except Exception as e:
            await handler.on_error(event, e)
            # Don't re-raise - let other handlers still run
            # The message is already acked to avoid blocking the queue
