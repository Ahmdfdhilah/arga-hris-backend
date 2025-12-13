"""
Event Handler Registry - Decorator-based handler registration

Provides @handles() decorator for mapping event types to handlers.
"""

from typing import Dict, List, Type, Callable
import logging

from app.core.messaging.consumer.base import BaseEventHandler

logger = logging.getLogger(__name__)


class EventHandlerRegistry:
    """
    Central registry mapping event types to handlers.
    
    Usage:
        @EventHandlerRegistry.register("user.created")
        class UserCreatedHandler(BaseEventHandler):
            ...
    
    Or with shorthand:
        @handles("user.created")
        class UserCreatedHandler(BaseEventHandler):
            ...
    """
    
    _handlers: Dict[str, List[Type[BaseEventHandler]]] = {}
    _initialized: bool = False
    
    @classmethod
    def register(cls, event_type: str) -> Callable:
        """
        Decorator to register a handler class for an event type.
        
        Multiple handlers can be registered for the same event type.
        They will all be called in registration order.
        
        Args:
            event_type: The event to handle (e.g. "user.created")
            
        Returns:
            Decorator function
        """
        def decorator(handler_class: Type[BaseEventHandler]) -> Type[BaseEventHandler]:
            if event_type not in cls._handlers:
                cls._handlers[event_type] = []
            
            # Avoid duplicate registration
            if handler_class not in cls._handlers[event_type]:
                cls._handlers[event_type].append(handler_class)
                logger.info(
                    f"Registered handler: {handler_class.__name__} → {event_type}"
                )
            
            return handler_class
        
        return decorator
    
    @classmethod
    def get_handlers(cls, event_type: str) -> List[Type[BaseEventHandler]]:
        """
        Get all handlers registered for an event type.
        
        Args:
            event_type: The event type to look up
            
        Returns:
            List of handler classes (empty if none registered)
        """
        return cls._handlers.get(event_type, [])
    
    @classmethod
    def get_all_event_types(cls) -> List[str]:
        """Get all registered event types."""
        return list(cls._handlers.keys())
    
    @classmethod
    def list_all(cls) -> Dict[str, List[str]]:
        """
        List all registered handlers.
        
        Returns:
            Dict mapping event types to handler class names
        """
        return {
            event: [h.__name__ for h in handlers]
            for event, handlers in cls._handlers.items()
        }
    
    @classmethod
    def clear(cls) -> None:
        """Clear all registrations. Useful for testing."""
        cls._handlers.clear()
        cls._initialized = False


# Convenience decorator alias
def handles(event_type: str) -> Callable:
    """
    Shorthand decorator to register an event handler.
    
    Example:
        @handles("user.created")
        class UserCreatedHandler(BaseEventHandler):
            async def handle(self, event: DomainEvent) -> None:
                ...
    """
    return EventHandlerRegistry.register(event_type)
