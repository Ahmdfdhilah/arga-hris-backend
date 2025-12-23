
from app.core.messaging.consumer.topology import Binding

# Define what this module needs from RabbitMQ
# This file is auto-discovered or manually imported by lifespan
bindings = [
    Binding(
        queue_name="hris_backend_user_events",
        exchange_name="sso.events",
        routing_keys=["user.*"],
        durable=True
    )
]
