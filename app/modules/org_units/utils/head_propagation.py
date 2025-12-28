"""
OrgUnit Head Propagation Utility
Handles supervisor assignment when org unit head changes.
"""

from typing import Optional
import logging

from app.modules.org_units.repositories import OrgUnitQueries, OrgUnitCommands
from app.modules.employees.repositories import EmployeeQueries, EmployeeCommands

logger = logging.getLogger(__name__)


class OrgUnitHeadUtil:
    """Utility for handling org unit head changes and supervisor propagation"""

    @staticmethod
    async def handle_head_change(
        org_queries: OrgUnitQueries,
        org_commands: OrgUnitCommands,
        emp_queries: EmployeeQueries,
        emp_commands: EmployeeCommands,
        org_unit_id: int,
        old_head_id: Optional[int],
        new_head_id: Optional[int],
        updated_by: str,
    ) -> list[int]:
        """
        Handle Org Unit Head change:
        - Update direct subordinates' supervisor_id
        - If Head cleared, resolve effective supervisor from parent
        - Propagate to child Org Units that don't have their own Head

        Returns:
            list[int]: List of affected employee IDs whose supervisor_id was updated
        """
        affected_employee_ids = []
        effective_supervisor_id = new_head_id
        if not effective_supervisor_id:
            effective_supervisor_id = await OrgUnitHeadUtil.resolve_supervisor_for_unit(
                org_queries, org_unit_id
            )

        members, _ = await emp_queries.list(org_unit_id=org_unit_id, limit=1000)
        logger.info(
            f"Updating {len(members)} members for OrgUnit {org_unit_id}. Effective Sup: {effective_supervisor_id}"
        )

        for emp in members:
            target_sup = effective_supervisor_id

            if target_sup == emp.id:
                logger.info(
                    f"Employee {emp.id} is the generic supervisor. Re-resolving excluding self."
                )
                target_sup = await OrgUnitHeadUtil.resolve_supervisor_for_unit(
                    org_queries, org_unit_id, exclude_employee_id=emp.id
                )
                logger.info(f"Re-resolved supervisor for {emp.id}: {target_sup}")

            if emp.supervisor_id != target_sup:
                logger.info(
                    f"Updating Employee {emp.id}: supervisor {emp.supervisor_id} -> {target_sup}"
                )
                emp.supervisor_id = target_sup
                emp.set_updated_by(updated_by)
                await emp_commands.update(emp)
                affected_employee_ids.append(emp.id)

        children, _ = await org_queries.get_children(org_unit_id, recursive=False)
        for child in children:
            if not child.head_id:
                child_affected = await OrgUnitHeadUtil.handle_head_change(
                    org_queries, org_commands, emp_queries, emp_commands,
                    child.id, None, None, updated_by
                )
                affected_employee_ids.extend(child_affected)

        return affected_employee_ids

    @staticmethod
    async def resolve_supervisor_for_unit(
        queries: OrgUnitQueries,
        org_unit_id: int,
        exclude_employee_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Resolve effective supervisor for a unit by looking up the hierarchy.
        If exclude_employee_id is provided, skips that employee if found as head.
        """
        current_unit = await queries.get_by_id(org_unit_id)
        while current_unit:
            logger.info(
                f"Resolving sup for Unit {org_unit_id}. "
                f"Checking Unit {current_unit.id}. Head: {current_unit.head_id}. "
                f"Exclude: {exclude_employee_id}"
            )
            if current_unit.head_id:
                if exclude_employee_id is None or current_unit.head_id != exclude_employee_id:
                    return current_unit.head_id
                else:
                    logger.info("Skipping head because matches exclude_employee_id")

            if not current_unit.parent_id:
                break
            current_unit = await queries.get_by_id(current_unit.parent_id)
        return None
