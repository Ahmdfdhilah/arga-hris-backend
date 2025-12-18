from typing import List, Dict, Any, Tuple, Optional
from datetime import date
from app.modules.work_submissions.schemas.responses import (
    WorkSubmissionResponse,
    WorkSubmissionListResponse,
)
from app.modules.work_submissions.schemas.shared import SubmissionStatus, FileMetadata
from app.modules.work_submissions.repositories import WorkSubmissionQueries
from app.modules.employees.repositories import EmployeeQueries
from app.core.utils.file_upload import generate_signed_url_for_path


class ListMySubmissionsUseCase:
    def __init__(self, queries: WorkSubmissionQueries):
        self.queries = queries

    def _convert_files_paths_to_urls(
        self, files_metadata: List[Dict[str, Any]]
    ) -> List[FileMetadata]:
        files_with_urls: List[FileMetadata] = []
        for file_meta in files_metadata:
            file_path = file_meta.get("file_path")
            file_name = file_meta.get("file_name")
            file_size = file_meta.get("file_size")
            file_type = file_meta.get("file_type")

            if not file_path or not file_name or file_size is None or not file_type:
                continue

            signed_url = generate_signed_url_for_path(file_path)
            if signed_url:
                files_with_urls.append(
                    FileMetadata(
                        file_name=file_name,
                        file_url=signed_url,
                        file_size=file_size,
                        file_type=file_type,
                        file_path=file_path,
                    )
                )
        return files_with_urls

    async def execute(
        self,
        employee_id: int,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmissionResponse], int]:
        skip = (page - 1) * limit

        submissions, total = await self.queries.list_by_employee(
            employee_id=employee_id,
            submission_month=submission_month,
            status=status,
            skip=skip,
            limit=limit,
        )

        response_data: List[WorkSubmissionResponse] = []
        for submission in submissions:
            files_with_urls = self._convert_files_paths_to_urls(submission.files or [])
            response_data.append(
                WorkSubmissionResponse(
                    id=submission.id,
                    employee_id=submission.employee_id,
                    submission_month=submission.submission_month,
                    title=submission.title,
                    description=submission.description,
                    files=files_with_urls,
                    status=SubmissionStatus(submission.status),
                    submitted_at=submission.submitted_at,
                    created_by=submission.created_by,
                    created_at=submission.created_at,
                    updated_at=submission.updated_at,
                )
            )

        return response_data, total


class ListAllSubmissionsUseCase:
    def __init__(
        self,
        queries: WorkSubmissionQueries,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries

    async def _get_employee_dict(self, employee_id: int):
        emp = await self.employee_queries.get_by_id(employee_id)
        if not emp:
            return None
        return {
            "id": emp.id,
            "name": emp.user.name if emp.user else None,
            "employee_number": emp.employee_number,
        }

    async def execute(
        self,
        employee_id: Optional[int] = None,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmissionListResponse], int]:
        skip = (page - 1) * limit

        submissions, total = await self.queries.list_all(
            employee_id=employee_id,
            submission_month=submission_month,
            status=status,
            skip=skip,
            limit=limit,
        )

        response_data: List[WorkSubmissionListResponse] = []
        for submission in submissions:
            employee_name: Optional[str] = None
            employee_number: Optional[str] = None
            try:
                employee_info = await self._get_employee_dict(submission.employee_id)
                if employee_info:
                    employee_name = employee_info.get("name")
                    employee_number = employee_info.get("employee_number")
            except Exception:
                pass

            response_data.append(
                WorkSubmissionListResponse(
                    id=submission.id,
                    employee_id=submission.employee_id,
                    employee_name=employee_name,
                    employee_number=employee_number,
                    submission_month=submission.submission_month,
                    title=submission.title,
                    files_count=len(submission.files or []),
                    status=SubmissionStatus(submission.status),
                    submitted_at=submission.submitted_at,
                    created_at=submission.created_at,
                    updated_at=submission.updated_at,
                )
            )

        return response_data, total
