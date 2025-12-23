from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

@dataclass
class DomainEvent:
    """
    Standard event structure - shared across all services.
    """
    entity_type: str          # e.g., "user"
    event_action: str         # e.g., "created"
    entity_id: Any
    data: Dict[str, Any]
    timestamp: datetime
    source_service: str
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: int = 1
    
    def get_routing_key(self) -> str:
        """Get routing key format: 'user.created'"""
        return f"{self.entity_type}.{self.event_action}"
    
    @classmethod
    def from_dict(cls, body: Dict[str, Any]) -> "DomainEvent":
        """
        Robust parsing logic for incoming messages.
        Handles both separate and combined event_type formats.
        """
        timestamp_str = body.get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.utcnow()

        # Parse event type logic
        event_type_str = body.get("event_type", "")
        entity_type = body.get("entity_type", "")
        event_action = ""

        # If publisher sends combined string in event_type (e.g., "user.created")
        # and didn't provide separate fields
        if not entity_type and "." in event_type_str:
            parts = event_type_str.split(".", 1)
            entity_type = parts[0]
            event_action = parts[1]
        else:
            # Fallback or standard usage
            event_action = event_type_str

        return cls(
            entity_type=entity_type,
            event_action=event_action,
            entity_id=body.get("entity_id"),
            data=body.get("data", {}),
            timestamp=timestamp,
            source_service=body.get("source", body.get("source_service", "unknown")),
            correlation_id=body.get("correlation_id", ""),
            version=body.get("version", 1),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "event_type": self.event_action, # Published as event_type typically
            "entity_id": self.entity_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source_service,
            "correlation_id": self.correlation_id,
            "version": self.version,
        }
