from typing import List, Tuple
from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries
from app.core.exceptions import NotFoundException


class ListSubordinatesUseCase:
    """Use Case for listing subordinates."""

    def __init__(self, queries: EmployeeQueries):
        self.queries = queries

    async def execute(
        self,
        employee_id: int,
        page: int = 1,
        limit: int = 10,
        recursive: bool = False,
    ) -> Tuple[List[Employee], int]:
        """Returns (items, total_count)"""
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")

        skip = (page - 1) * limit

        employees, total = await self.queries.get_subordinates(
            supervisor_id=employee_id,
            recursive=recursive,
            skip=skip,
            limit=limit,
        )
        return employees, total
