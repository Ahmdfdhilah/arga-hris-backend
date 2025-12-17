"""
Base Event Handler - Abstract class for all event handlers

All handlers MUST be idempotent.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional
from datetime import datetime
import logging


@dataclass
class DomainEvent:
    """
    Standard event structure - shared across all services.
    
    Fields match publisher format:
    - entity_type: Domain entity (farmer, user, employee)
    - event_action: Action type (created, updated, deleted)
    
    Attributes:
        entity_type: Entity domain (e.g. "user", "farmer")
        event_action: Action (e.g. "created", "updated", "deleted")
        entity_id: Primary key of the entity
        data: Event payload
        timestamp: When event occurred
        source_service: Service that published the event
        correlation_id: For distributed tracing
        version: Schema version for compatibility
    """
    entity_type: str          # e.g., "user"
    event_action: str         # e.g., "created"
    entity_id: Any
    data: Dict[str, Any]
    timestamp: datetime
    source_service: str
    correlation_id: str = ""
    version: int = 1
    
    def get_routing_key(self) -> str:
        """Get routing key format: 'user.created'"""
        return f"{self.entity_type}.{self.event_action}"


class BaseEventHandler(ABC):
    """
    Abstract base class for all event handlers.
    
    Rules:
    1. Handlers MUST be idempotent (safe to retry)
    2. Handlers should use upsert patterns
    3. Handlers should not throw - log and continue
    
    Example:
        @handles("user.created")
        class UserCreatedHandler(BaseEventHandler):
            async def handle(self, event: DomainEvent) -> None:
                await repo.sync_from_sso(
                    sso_id=event.entity_id,
                    name=event.data.get("name"),
                )
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """
        Process the event.
        
        MUST be idempotent - receiving the same event twice
        should not cause errors or duplicate data.
        """
        pass
    
    async def can_handle(self, event: DomainEvent) -> bool:
        """
        Optional filter - return False to skip this handler.
        
        Useful for conditional handling based on event data.
        """
        return True
    
    async def on_success(self, event: DomainEvent) -> None:
        """Called after successful handling."""
        self.logger.info(f"Handled {event.get_routing_key()} for entity {event.entity_id}")
    
    async def on_error(self, event: DomainEvent, error: Exception) -> None:
        """
        Called when handler fails.
        
        Override for custom error handling (e.g., alerting).
        """
        self.logger.error(
            f"Handler failed for {event.get_routing_key()}: {error}",
            exc_info=True,
            extra={
                "entity_type": event.entity_type,
                "event_action": event.event_action,
                "entity_id": event.entity_id,
                "source": event.source_service,
            }
        )
