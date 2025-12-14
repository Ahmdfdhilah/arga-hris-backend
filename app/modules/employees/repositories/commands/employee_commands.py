"""
Employee Command Repository - Write operations
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.core.utils.datetime import get_utc_now
from app.modules.employees.models.employee import Employee


class EmployeeCommands:
    """Write operations for Employee model"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, employee: Employee) -> Employee:
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def update(self, employee: Employee) -> Employee:
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def delete(self, employee_id: int, user_id: int) -> bool:
        from app.modules.employees.repositories.queries import EmployeeQueries
        
        queries = EmployeeQueries(self.db)
        employee = await queries.get_by_id(employee_id)
        if not employee:
            return False

        employee.deleted_at = get_utc_now()
        employee.deleted_by = user_id
        employee.is_active = False
        await self.db.commit()
        return True

    async def hard_delete(self, employee_id: int) -> bool:
        from app.modules.employees.repositories.queries import EmployeeQueries
        
        queries = EmployeeQueries(self.db)
        employee = await queries.get_by_id_with_deleted(employee_id)
        if not employee:
            return False

        await self.db.delete(employee)
        await self.db.commit()
        return True

    async def restore(self, employee_id: int) -> Optional[Employee]:
        from app.modules.employees.repositories.queries import EmployeeQueries
        
        queries = EmployeeQueries(self.db)
        employee = await queries.get_by_id_with_deleted(employee_id)
        if not employee or not employee.is_deleted():
            return None

        employee.deleted_at = None
        employee.deleted_by = None
        employee.is_active = True
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def bulk_update_supervisor(
        self,
        employee_ids: List[int],
        new_supervisor_id: Optional[int],
        updated_by: int
    ) -> int:
        result = await self.db.execute(
            update(Employee)
            .where(Employee.id.in_(employee_ids))
            .values(supervisor_id=new_supervisor_id, updated_by=updated_by)
        )
        await self.db.commit()
        return result.rowcount
