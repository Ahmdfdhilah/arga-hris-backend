"""
Attendance Command Repository - Write operations
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendances.models.attendances import Attendance


class AttendanceCommands:
    """Write operations for Attendance"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Attendance:
        attendance = Attendance(**data)
        self.db.add(attendance)
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance

    async def update(self, attendance_id: int, data: Dict[str, Any]) -> Optional[Attendance]:
        from app.modules.attendance.repositories.queries import AttendanceQueries
        
        queries = AttendanceQueries(self.db)
        attendance = await queries.get_by_id(attendance_id)
        if not attendance:
            return None
        
        for key, value in data.items():
            setattr(attendance, key, value)
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance

    async def delete(self, attendance_id: int) -> bool:
        from app.modules.attendance.repositories.queries import AttendanceQueries
        
        queries = AttendanceQueries(self.db)
        attendance = await queries.get_by_id(attendance_id)
        if not attendance:
            return False
        
        await self.db.delete(attendance)
        await self.db.commit()
        return True
