from typing import Optional
import logging
from app.modules.org_units.repositories import OrgUnitQueries

logger = logging.getLogger(__name__)


class SupervisorAssignmentUtil:
    """Utility for resolving supervisor based on org unit hierarchy"""

    @staticmethod
    async def resolve_supervisor(
        org_unit_queries: OrgUnitQueries,
        org_unit_id: int,
        exclude_employee_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Resolve supervisor by traversing Org Unit hierarchy upwards.
        - If current unit has Head (and Head != me), return Head.
        - Else, go to Parent Unit and repeat.
        - If Root reached with no head, return None.
        """
        current_unit = await org_unit_queries.get_by_id(org_unit_id)
        while current_unit:
            # Check if unit has head
            if current_unit.head_id:
                # Check exclusion (e.g. do not report to self)
                if (
                    exclude_employee_id is None
                    or current_unit.head_id != exclude_employee_id
                ):
                    return current_unit.head_id

            # Move to parent
            if not current_unit.parent_id:
                break

            current_unit = await org_unit_queries.get_by_id(current_unit.parent_id)

        return None
