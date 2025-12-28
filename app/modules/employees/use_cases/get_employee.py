from typing import Optional
from app.modules.employees.models.employee import Employee
from app.modules.employees.repositories import EmployeeQueries
from app.core.exceptions import NotFoundException


class GetEmployeeUseCase:
    """Use Case for retrieving an employee by ID."""

    def __init__(self, queries: EmployeeQueries):
        self.queries = queries

    async def execute(self, employee_id: int) -> Employee:
        employee = await self.queries.get_by_id(employee_id)
        if not employee:
            raise NotFoundException(f"Employee with ID {employee_id} not found")
        return employee


class GetEmployeeByCodeUseCase:
    """Use Case for retrieving an employee by code."""

    def __init__(self, queries: EmployeeQueries):
        self.queries = queries

    async def execute(self, code: str) -> Optional[Employee]:
        return await self.queries.get_by_code(code)


class GetEmployeeByEmailUseCase:
    """Use Case for retrieving an employee by email."""

    def __init__(self, queries: EmployeeQueries):
        self.queries = queries

    async def execute(self, email: str) -> Optional[Employee]:
        return await self.queries.get_by_email(email)
