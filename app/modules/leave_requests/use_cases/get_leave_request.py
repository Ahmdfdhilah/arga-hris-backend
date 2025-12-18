from app.modules.leave_requests.schemas.responses import LeaveRequestResponse
from app.modules.leave_requests.repositories import LeaveRequestQueries
from app.core.exceptions import NotFoundException


class GetLeaveRequestUseCase:
    def __init__(self, queries: LeaveRequestQueries):
        self.queries = queries

    async def execute(self, leave_request_id: int) -> LeaveRequestResponse:
        leave_request = await self.queries.get_by_id(leave_request_id)

        if not leave_request:
            raise NotFoundException(
                f"Leave request dengan ID {leave_request_id} tidak ditemukan"
            )

        return LeaveRequestResponse.model_validate(leave_request)
