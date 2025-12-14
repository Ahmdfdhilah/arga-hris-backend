"""
LeaveRequest Command Repository - Write operations
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.leave_requests.models.leave_request import LeaveRequest


class LeaveRequestCommands:
    """Write operations for LeaveRequest"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> LeaveRequest:
        leave_request = LeaveRequest(**data)
        self.db.add(leave_request)
        await self.db.commit()
        await self.db.refresh(leave_request)
        return leave_request

    async def update(self, leave_request_id: int, data: Dict[str, Any]) -> Optional[LeaveRequest]:
        from app.modules.leave_requests.repositories.queries import LeaveRequestQueries
        
        queries = LeaveRequestQueries(self.db)
        leave_request = await queries.get_by_id(leave_request_id)
        if not leave_request:
            return None
        
        for key, value in data.items():
            setattr(leave_request, key, value)
        await self.db.commit()
        await self.db.refresh(leave_request)
        return leave_request

    async def delete(self, leave_request_id: int) -> bool:
        from app.modules.leave_requests.repositories.queries import LeaveRequestQueries
        
        queries = LeaveRequestQueries(self.db)
        leave_request = await queries.get_by_id(leave_request_id)
        if not leave_request:
            return False
        
        await self.db.delete(leave_request)
        await self.db.commit()
        return True
