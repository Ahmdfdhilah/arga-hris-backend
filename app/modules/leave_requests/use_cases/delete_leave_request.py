from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.leave_requests.repositories import (
    LeaveRequestQueries,
    LeaveRequestCommands,
)
from app.core.exceptions import NotFoundException
from app.modules.attendances.utils.attendance_leave_sync import revert_attendances_from_leave


class DeleteLeaveRequestUseCase:
    def __init__(
        self,
        db: AsyncSession,
        queries: LeaveRequestQueries,
        commands: LeaveRequestCommands,
    ):
        self.db = db
        self.queries = queries
        self.commands = commands

    async def execute(self, leave_request_id: int) -> None:
        leave_request = await self.queries.get_by_id(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        # Revert attendance records from 'leave' to 'absent' before deleting
        await revert_attendances_from_leave(
            db=self.db,
            employee_id=leave_request.employee_id,
            start_date=leave_request.start_date,
            end_date=leave_request.end_date,
        )

        await self.commands.delete(leave_request_id)
