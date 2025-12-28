from typing import List, Tuple
from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries
from app.modules.org_units.repositories import OrgUnitQueries
from app.core.exceptions import NotFoundException


class ListByOrgUnitUseCase:
    """Use Case for listing employees by org unit."""

    def __init__(self, queries: EmployeeQueries, org_unit_queries: OrgUnitQueries):
        self.queries = queries
        self.org_unit_queries = org_unit_queries

    async def execute(
        self,
        org_unit_id: int,
        page: int = 1,
        limit: int = 10,
        include_children: bool = False,
    ) -> Tuple[List[Employee], int]:
        """Returns (items, total_count)"""
        org_unit = await self.org_unit_queries.get_by_id(org_unit_id)
        if not org_unit:
            raise NotFoundException(f"OrgUnit with ID {org_unit_id} not found")

        skip = (page - 1) * limit

        employees, total = await self.queries.get_all_by_org_unit(
            org_unit_id=org_unit_id,
            include_children=include_children,
            skip=skip,
            limit=limit,
        )
        return employees, total
