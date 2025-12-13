"""
Domain Event Definitions

Standard event format for all HRIS domain events published to RabbitMQ.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
import uuid
import json
from app.core.enums.event_type import EventType


@dataclass
class DomainEvent:
    """
    Standard domain event format for publishing to RabbitMQ.
    
    All events follow this structure for consistency across services.
    """
    event_type: EventType
    entity_type: str  # e.g., "employee", "org_unit"
    entity_id: int
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.utcnow())
    source: str = "hris"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0"
    
    @property
    def routing_key(self) -> str:
        """Generate routing key for RabbitMQ topic exchange"""
        return f"{self.entity_type}.{self.event_type.value}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "event_type": self.event_type.value,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id,
            "version": self.version,
        }
    
    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """Create event from dictionary"""
        return cls(
            event_type=EventType(data["event_type"]),
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data.get("source", "unknown"),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
            version=data.get("version", "1.0"),
        )


def create_employee_event(
    event_type: EventType,
    employee_id: int,
    data: Dict[str, Any],
    correlation_id: Optional[str] = None
) -> DomainEvent:
    """Helper to create employee events"""
    return DomainEvent(
        event_type=event_type,
        entity_type="employee",
        entity_id=employee_id,
        data=data,
        correlation_id=correlation_id or str(uuid.uuid4()),
    )


def create_org_unit_event(
    event_type: EventType,
    org_unit_id: int,
    data: Dict[str, Any],
    correlation_id: Optional[str] = None
) -> DomainEvent:
    """Helper to create org unit events"""
    return DomainEvent(
        event_type=event_type,
        entity_type="org_unit",
        entity_id=org_unit_id,
        data=data,
        correlation_id=correlation_id or str(uuid.uuid4()),
    )
