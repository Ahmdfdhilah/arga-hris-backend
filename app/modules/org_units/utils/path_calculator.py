"""
OrgUnit Path Calculator Utility
Handles path and level recalculation for org unit hierarchy.
"""

from typing import Optional
import logging

from app.modules.org_units.models.org_unit import OrgUnit
from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands

logger = logging.getLogger(__name__)


class OrgUnitPathUtil:
    """Utility for calculating and updating org unit paths"""

    @staticmethod
    async def recalculate_path(
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        org_unit: OrgUnit,
    ) -> list[int]:
        """
        Recalculate path for org unit and all its descendants.
        Called when parent_id changes.

        Returns:
            list[int]: List of affected org unit IDs whose path was updated
        """
        affected_org_unit_ids = []
        old_path = org_unit.path

        if org_unit.parent_id:
            parent = await queries.get_by_id(org_unit.parent_id)
            if parent:
                org_unit.path = f"{parent.path}.{org_unit.id}"
                org_unit.level = parent.level + 1
                await commands.update(org_unit)

                descendants = await OrgUnitPathUtil._update_descendants(
                    queries, commands, org_unit, old_path
                )
                affected_org_unit_ids.extend(descendants)
        else:
            org_unit.path = str(org_unit.id)
            org_unit.level = 1
            await commands.update(org_unit)

        return affected_org_unit_ids

    @staticmethod
    async def _update_descendants(
        queries: OrgUnitQueries,
        commands: OrgUnitCommands,
        org_unit: OrgUnit,
        old_path: str,
    ) -> list[int]:
        """
        Update path/level for all descendants after parent path change

        Returns:
            list[int]: List of affected descendant org unit IDs
        """
        affected_ids = []
        children, _ = await queries.get_children(
            org_unit.id, recursive=True, skip=0, limit=1000
        )
        for child in children:
            child.path = child.path.replace(old_path, org_unit.path, 1)
            parts = child.path.split(".")
            child.level = len(parts)
            await commands.update(child)
            affected_ids.append(child.id)

        return affected_ids

    @staticmethod
    def build_initial_path(parent: Optional[OrgUnit], org_unit_id: int) -> tuple[str, int]:
        """Build initial path and level for new org unit"""
        if parent:
            path = f"{parent.path}.{org_unit_id}"
            level = parent.level + 1
        else:
            path = str(org_unit_id)
            level = 1
        return path, level
