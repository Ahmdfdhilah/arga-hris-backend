"""Organization Unit Type Enum."""

from enum import Enum


class OrgUnitType(str, Enum):
    """Organization unit types."""
    DIREKTORAT = "Direktorat"
    MANAGERIAL = "Managerial"
    OPERASIONAL = "Operasional"
