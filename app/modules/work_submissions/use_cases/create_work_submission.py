from datetime import date
from app.modules.work_submissions.schemas.requests import WorkSubmissionCreateRequest
from app.modules.work_submissions.schemas.responses import WorkSubmissionResponse
from app.modules.work_submissions.schemas.shared import SubmissionStatus
from app.modules.work_submissions.repositories import (
    WorkSubmissionQueries,
    WorkSubmissionCommands,
)
from app.core.exceptions.client_error import ConflictException
from app.core.utils.datetime import get_utc_now


class CreateWorkSubmissionUseCase:
    def __init__(
        self,
        queries: WorkSubmissionQueries,
        commands: WorkSubmissionCommands,
    ):
        self.queries = queries
        self.commands = commands

    async def execute(
        self, request: WorkSubmissionCreateRequest, created_by_user_id: int
    ) -> WorkSubmissionResponse:
        normalized_month = date(
            request.submission_month.year, request.submission_month.month, 1
        )

        existing = await self.queries.check_existing(
            employee_id=request.employee_id,
            submission_month=normalized_month,
        )

        if existing:
            raise ConflictException(
                f"Submission untuk employee {request.employee_id} bulan {normalized_month.strftime('%B %Y')} sudah ada"
            )

        submission_data = {
            "employee_id": request.employee_id,
            "submission_month": normalized_month,
            "title": request.title,
            "description": request.description,
            "files": [],
            "status": request.status.value,
            "submitted_at": (
                get_utc_now() if request.status.value == "submitted" else None
            ),
            "created_by": created_by_user_id,
        }

        submission = await self.commands.create(submission_data)

        # No files initially
        return WorkSubmissionResponse(
            id=submission.id,
            employee_id=submission.employee_id,
            submission_month=submission.submission_month,
            title=submission.title,
            description=submission.description,
            files=[],
            status=SubmissionStatus(submission.status),
            submitted_at=submission.submitted_at,
            created_by=submission.created_by,
            created_at=submission.created_at,
            updated_at=submission.updated_at,
        )
