from typing import Optional, List, Tuple
from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries


class ListEmployeesUseCase:
    """Use Case for listing employees with filtering and pagination."""

    def __init__(self, queries: EmployeeQueries):
        self.queries = queries

    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        org_unit_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Employee], int]:
        """Returns (items, total_count)"""
        skip = (page - 1) * limit

        employees, total = await self.queries.list(
            org_unit_id=org_unit_id,
            is_active=is_active,
            search=search,
            skip=skip,
            limit=limit,
        )
        return employees, total


class ListDeletedEmployeesUseCase:
    """Use Case for listing deleted employees."""

    def __init__(self, queries: EmployeeQueries):
        self.queries = queries

    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
    ) -> Tuple[List[Employee], int]:
        """Returns (items, total_count)"""
        skip = (page - 1) * limit

        employees, total = await self.queries.list_deleted(
            search=search,
            skip=skip,
            limit=limit,
        )
        return employees, total
