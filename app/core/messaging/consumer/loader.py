
import importlib
import logging
from .topology import TopologyConfig

logger = logging.getLogger(__name__)

def load_module_bindings(modules: list[str]) -> None:
    """
    Import bindings from specified modules and register them.
    Expects module to have an 'events.bindings' submodule with a 'bindings' list.
    """
    for module_path in modules:
        try:
            # e.g. app.modules.users.users -> app.modules.users.users.events.bindings
            binding_module = f"{module_path}.events.bindings"
            mod = importlib.import_module(binding_module)
            
            if hasattr(mod, "bindings"):
                TopologyConfig.register(mod.bindings)
                logger.debug(f"Loaded bindings from {binding_module}")
            else:
                logger.warning(f"No 'bindings' list found in {binding_module}")
                
        except ImportError as e:
            logger.warning(f"Could not load bindings for {module_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading bindings for {module_path}: {e}")
