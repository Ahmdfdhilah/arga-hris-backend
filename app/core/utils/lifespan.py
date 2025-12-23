"""
Application lifespan management.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.tasks.scheduler_startup import setup_scheduler, shutdown_scheduler
from app.core.messaging import message_engine
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

    from app.core.messaging.consumer import EventHandlerRegistry
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

    # Startup: RabbitMQ & Event Processing
    logger.info("Initializing RabbitMQ & Messaging Topology...")
    try:
        # 1. Load Bindings from Modules
        from app.core.messaging.consumer.loader import load_module_bindings
        load_module_bindings([
            "app.modules.users.users", # Users module
        ])

        # 2. Apply Topology (Exchanges, Queues, Bindings)
        from app.core.messaging import message_engine, EventProcessor
        
        await message_engine.connect()
        await message_engine.apply_topology()
        logger.info("RabbitMQ Topology applied successfully")

        # 3. Start Event Processor Loop
        # Note: Queue name is now derived from topology or hardcoded if simple
        # For now, we start one processor for the main service queue
        consumer = EventProcessor(service_name="hris")
        # We assume the user module binding created this queue
        await consumer.start_background(queue_name="hris_backend_user_events") # Must match binding
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
        await message_engine.disconnect()
        logger.info("RabbitMQ disconnected")
    except Exception as e:
        logger.warning(f"RabbitMQ disconnect error: {e}")

    # Shutdown: Stop scheduler
    logger.info("Stopping scheduler...")
    await shutdown_scheduler()
    logger.info("Scheduler stopped")
