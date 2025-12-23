from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Binding:
    """
    Represents a specific binding requirement for a module.
    Ex: User module needs to listen to 'sso.events' for 'user.*'
    """
    queue_name: str
    exchange_name: str
    routing_keys: List[str]
    durable: bool = True
    dead_letter: bool = True

class TopologyConfig:
    """
    Registry for all bindings required by the application.
    """
    _bindings: List[Binding] = []

    @classmethod
    def register(cls, bindings: List[Binding]):
        cls._bindings.extend(bindings)

    @classmethod
    def get_all_bindings(cls) -> List[Binding]:
        return cls._bindings
    
    @classmethod
    def clear(cls):
        cls._bindings = []
