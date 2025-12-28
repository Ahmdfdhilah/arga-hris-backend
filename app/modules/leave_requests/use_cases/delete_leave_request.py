from app.modules.leave_requests.repositories import (
    LeaveRequestQueries,
    LeaveRequestCommands,
)
from app.core.exceptions import NotFoundException


class DeleteLeaveRequestUseCase:
    def __init__(self, queries: LeaveRequestQueries, commands: LeaveRequestCommands):
        self.queries = queries
        self.commands = commands

    async def execute(self, leave_request_id: int) -> None:
        leave_request = await self.queries.get_by_id(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        await self.commands.delete(leave_request_id)
