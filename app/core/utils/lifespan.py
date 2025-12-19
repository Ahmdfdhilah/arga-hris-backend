"""
Application lifespan management.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.tasks.scheduler_startup import setup_scheduler, shutdown_scheduler
from app.core.messaging.rabbitmq import rabbitmq_manager
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager untuk startup dan shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None: Control back to the application
    """
    # Import event handlers to register them
    import app.modules.users.users.events  # noqa: F401 - registers handlers

    from app.core.messaging.consumer import EventConsumer, EventHandlerRegistry
    from app.grpc.server import grpc_server

    consumer = None

    # Startup: Scheduler
    logger.info("Starting scheduler...")
    await setup_scheduler()
    logger.info("Scheduler started successfully")

    # Startup: gRPC Server (for Employee/OrgUnit master data)
    logger.info("Starting gRPC server...")
    try:
        await grpc_server.start()
        logger.info("HRIS gRPC server started successfully")
    except Exception as e:
        logger.warning(
            f"gRPC server initialization failed: {e}. gRPC will not be available."
        )

    # Startup: RabbitMQ
    logger.info("Initializing RabbitMQ...")
    try:
        await rabbitmq_manager.connect()
        await rabbitmq_manager.setup_exchanges_and_queues()
        logger.info("RabbitMQ initialized successfully")

        # Log registered handlers
        all_handlers = EventHandlerRegistry.list_all()
        if all_handlers:
            logger.info("Registered event handlers:")
            for event_type, handlers in all_handlers.items():
                logger.info(f"  {event_type} → {', '.join(handlers)}")

        # Start event consumer in background
        consumer = EventConsumer(rabbitmq_manager, service_name="hris")
        consumer.start_background("hris.events", prefetch_count=10)
        logger.info("Event consumer started in background")

    except Exception as e:
        logger.warning(
            f"RabbitMQ initialization failed: {e}. Events will not be consumed."
        )

    yield

    # Shutdown: Event consumer
    logger.info("Stopping event consumer...")
    if consumer:
        try:
            await consumer.stop()
            logger.info("Event consumer stopped")
        except Exception as e:
            logger.warning(f"Event consumer stop error: {e}")

    # Shutdown: gRPC Server
    logger.info("Stopping gRPC server...")
    try:
        await grpc_server.stop()
        logger.info("gRPC server stopped")
    except Exception as e:
        logger.warning(f"gRPC server stop error: {e}")

    # Shutdown: RabbitMQ
    logger.info("Disconnecting RabbitMQ...")
    try:
        await rabbitmq_manager.disconnect()
        logger.info("RabbitMQ disconnected")
    except Exception as e:
        logger.warning(f"RabbitMQ disconnect error: {e}")

    # Shutdown: Stop scheduler
    logger.info("Stopping scheduler...")
    await shutdown_scheduler()
    logger.info("Scheduler stopped")
