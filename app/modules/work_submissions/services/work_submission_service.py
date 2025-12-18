from typing import Optional, List, Tuple
from datetime import date
from fastapi import UploadFile

from app.modules.work_submissions.repositories import (
    WorkSubmissionQueries,
    WorkSubmissionCommands,
)
from app.modules.employees.repositories import EmployeeQueries
from app.modules.work_submissions.schemas.requests import (
    WorkSubmissionCreateRequest,
    WorkSubmissionUpdateRequest,
)
from app.modules.work_submissions.schemas.responses import (
    WorkSubmissionResponse,
    WorkSubmissionListResponse,
)
from app.config.settings import settings

from app.modules.work_submissions.use_cases.create_work_submission import (
    CreateWorkSubmissionUseCase,
)
from app.modules.work_submissions.use_cases.get_work_submission import (
    GetWorkSubmissionUseCase,
)
from app.modules.work_submissions.use_cases.update_work_submission import (
    UpdateWorkSubmissionUseCase,
)
from app.modules.work_submissions.use_cases.delete_work_submission import (
    DeleteWorkSubmissionUseCase,
)
from app.modules.work_submissions.use_cases.list_work_submissions import (
    ListMySubmissionsUseCase,
    ListAllSubmissionsUseCase,
)


class WorkSubmissionService:
    """Facade Service for Work Submissions"""

    # Constants exposed for potential external usage if needed, though mostly used in Use Cases
    MAX_FILE_SIZE = settings.MAX_DOCUMENT_SIZE
    MAX_FILES_PER_SUBMISSION = 10

    def __init__(
        self,
        queries: WorkSubmissionQueries,
        commands: WorkSubmissionCommands,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries

        # Initialize Use Cases
        self.create_uc = CreateWorkSubmissionUseCase(queries, commands)
        self.get_uc = GetWorkSubmissionUseCase(queries)
        self.update_uc = UpdateWorkSubmissionUseCase(queries, commands)
        self.delete_uc = DeleteWorkSubmissionUseCase(queries, commands)
        self.list_my_uc = ListMySubmissionsUseCase(queries)
        self.list_all_uc = ListAllSubmissionsUseCase(queries, employee_queries)

    async def get_my_submissions(
        self,
        employee_id: int,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmissionResponse], int]:
        return await self.list_my_uc.execute(
            employee_id, submission_month, status, page, limit
        )

    async def create_submission(
        self,
        request: WorkSubmissionCreateRequest,
        created_by_user_id: int,
    ) -> WorkSubmissionResponse:
        return await self.create_uc.execute(request, created_by_user_id)

    async def get_submission_by_id(self, submission_id: int) -> WorkSubmissionResponse:
        return await self.get_uc.execute(submission_id)

    async def update_submission(
        self,
        submission_id: int,
        request: WorkSubmissionUpdateRequest,
    ) -> WorkSubmissionResponse:
        return await self.update_uc.execute_update(submission_id, request)

    async def delete_submission(self, submission_id: int) -> None:
        await self.delete_uc.execute(submission_id)

    async def upload_files(
        self,
        submission_id: int,
        files: List[UploadFile],
    ) -> WorkSubmissionResponse:
        return await self.update_uc.upload_files(submission_id, files)

    async def delete_file(
        self,
        submission_id: int,
        file_path: str,
    ) -> WorkSubmissionResponse:
        return await self.update_uc.delete_file(submission_id, file_path)

    async def list_all_submissions(
        self,
        employee_id: Optional[int] = None,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmissionListResponse], int]:
        return await self.list_all_uc.execute(
            employee_id, submission_month, status, page, limit
        )
