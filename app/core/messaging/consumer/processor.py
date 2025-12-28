
import asyncio
import json
import logging
from typing import Optional

from aio_pika.abc import AbstractIncomingMessage

from app.core.messaging.engine import message_engine
from app.core.messaging.types import DomainEvent
from app.core.messaging.consumer.registry import EventHandlerRegistry

logger = logging.getLogger(__name__)

class EventProcessor:
    """
    Main event processing loop.
    Decoupled from topology setup.
    """
    
    def __init__(self, service_name: str = "hris"):
        self.output_queue: Optional[str] = None
        self.service_name = service_name
        self.engine = message_engine
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self, queue_name: str) -> None:
        """
        Start processing messages from an EXISTING queue.
        Topology must be applied before calling this.
        """
        if self._running:
            return

        self.output_queue = queue_name
        try:
            channel = await self.engine.get_channel()
            # We assume queue exists because Engine applied topology
            queue = await channel.declare_queue(queue_name, durable=True, passive=True)
            
            self._running = True
            logger.info(f"Event Processor started on queue: {queue_name}")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    if not self._running:
                        break
                    await self._process_message(message)
                    
        except Exception as e:
            logger.error(f"Event Processor failed: {e}")
            self._running = False
            raise

    async def start_background(self, queue_name: str) -> asyncio.Task:
        self._task = asyncio.create_task(self.start(queue_name))
        return self._task

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Event Processor stopped")

    async def _process_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process(requeue=False):
            try:
                body = json.loads(message.body.decode())
                event = DomainEvent.from_dict(body)
                
                if event.source_service == self.service_name:
                    return

                handlers = EventHandlerRegistry.get_handlers(event.get_routing_key())
                if not handlers:
                    # Optional: Log warning or debug
                    return

                for handler_class in handlers:
                    handler = handler_class()
                    if await handler.can_handle(event):
                        await handler.handle(event)
                        await handler.on_success(event)

            except Exception as e:
                logger.error(f"Error processing message: {e}", exc_info=True)
                # Message is acked to prevent blocking; could add DLQ logic if needed manually
