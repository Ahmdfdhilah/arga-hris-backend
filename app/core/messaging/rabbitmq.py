"""
RabbitMQ Connection Manager

Manages RabbitMQ connections, channels, and exchange/queue setup.
Uses aio-pika for async operations.
"""

import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

import aio_pika
from aio_pika import Channel, Connection, ExchangeType, Message
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractExchange

from app.config.settings import settings

logger = logging.getLogger(__name__)


class RabbitMQManager:
    """
    RabbitMQ connection and channel manager.
    
    Features:
    - Connection pooling with auto-reconnect
    - Exchange and queue declaration
    - Dead letter exchange (DLX) support
    """
    
    # Exchange names
    HRIS_EXCHANGE = "hris.events"
    DLX_EXCHANGE = "hris.dlx"
    
    # Queue names
    DLQ_QUEUE = "hris.dlq"
    
    def __init__(self):
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._exchange: Optional[AbstractExchange] = None
        self._dlx_exchange: Optional[AbstractExchange] = None
        self._lock = asyncio.Lock()
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        return self._connected and self._connection is not None and not self._connection.is_closed
    
    async def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        if self.is_connected:
            return
        
        async with self._lock:
            if self.is_connected:
                return
            
            try:
                logger.info(f"Connecting to RabbitMQ at {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
                
                self._connection = await aio_pika.connect_robust(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    login=settings.RABBITMQ_USER,
                    password=settings.RABBITMQ_PASSWORD,
                    virtualhost=settings.RABBITMQ_VHOST,
                )
                
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=10)
                
                self._connected = True
                logger.info("RabbitMQ connection established")
                
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                self._connected = False
                raise
    
    async def disconnect(self) -> None:
        """Close RabbitMQ connection"""
        async with self._lock:
            if self._channel and not self._channel.is_closed:
                await self._channel.close()
            
            if self._connection and not self._connection.is_closed:
                await self._connection.close()
            
            self._connection = None
            self._channel = None
            self._exchange = None
            self._dlx_exchange = None
            self._connected = False
            
            logger.info("RabbitMQ connection closed")
    
    async def setup_exchanges_and_queues(self) -> None:
        """
        Declare exchanges and queues for HRIS events.
        
        Creates:
        - hris.events (topic exchange) - main event exchange
        - hris.dlx (direct exchange) - dead letter exchange
        - hris.dlq (queue) - dead letter queue
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            # Dead Letter Exchange (DLX)
            self._dlx_exchange = await self._channel.declare_exchange(
                self.DLX_EXCHANGE,
                ExchangeType.DIRECT,
                durable=True,
            )
            
            # Dead Letter Queue
            dlq = await self._channel.declare_queue(
                self.DLQ_QUEUE,
                durable=True,
            )
            await dlq.bind(self._dlx_exchange, routing_key="dead-letter")
            
            # Main HRIS Events Exchange (topic for flexible routing)
            self._exchange = await self._channel.declare_exchange(
                self.HRIS_EXCHANGE,
                ExchangeType.TOPIC,
                durable=True,
            )
            
            logger.info(f"Exchanges and queues setup complete: {self.HRIS_EXCHANGE}, {self.DLX_EXCHANGE}")
            
        except Exception as e:
            logger.error(f"Failed to setup exchanges/queues: {e}")
            raise
    
    async def get_channel(self) -> AbstractChannel:
        """Get the current channel, reconnecting if necessary"""
        if not self.is_connected:
            await self.connect()
        return self._channel
    
    async def get_exchange(self) -> AbstractExchange:
        """Get the main HRIS events exchange"""
        if not self._exchange:
            await self.setup_exchanges_and_queues()
        return self._exchange
    
    async def declare_consumer_queue(
        self,
        queue_name: str,
        routing_keys: list[str],
        durable: bool = True,
        with_dlq: bool = True,
    ) -> aio_pika.Queue:
        """
        Declare a consumer queue bound to the HRIS exchange.
        
        Args:
            queue_name: Name of the queue
            routing_keys: List of routing keys to bind (e.g., ["employee.*", "org_unit.created"])
            durable: Whether queue survives broker restart
            with_dlq: Whether to enable dead letter queue for this queue
        
        Returns:
            Declared queue
        """
        if not self.is_connected:
            await self.connect()
        
        arguments = {}
        if with_dlq:
            arguments["x-dead-letter-exchange"] = self.DLX_EXCHANGE
            arguments["x-dead-letter-routing-key"] = "dead-letter"
        
        queue = await self._channel.declare_queue(
            queue_name,
            durable=durable,
            arguments=arguments if arguments else None,
        )
        
        exchange = await self.get_exchange()
        for routing_key in routing_keys:
            await queue.bind(exchange, routing_key=routing_key)
            logger.info(f"Queue {queue_name} bound to {routing_key}")
        
        return queue


# Global singleton instance
rabbitmq_manager = RabbitMQManager()
