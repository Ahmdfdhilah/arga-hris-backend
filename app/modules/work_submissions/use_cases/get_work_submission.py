from typing import List, Dict, Any
from app.modules.work_submissions.schemas.responses import WorkSubmissionResponse
from app.modules.work_submissions.schemas.shared import SubmissionStatus, FileMetadata
from app.modules.work_submissions.repositories import WorkSubmissionQueries
from app.core.exceptions.client_error import NotFoundException
from app.core.utils.file_upload import generate_signed_url_for_path


class GetWorkSubmissionUseCase:
    def __init__(self, queries: WorkSubmissionQueries):
        self.queries = queries

    def _convert_files_paths_to_urls(
        self, files_metadata: List[Dict[str, Any]]
    ) -> List[FileMetadata]:
        """Convert file paths to signed URLs."""
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

    async def execute(self, submission_id: int) -> WorkSubmissionResponse:
        submission = await self.queries.get_by_id(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        files_with_urls = self._convert_files_paths_to_urls(submission.files or [])

        return WorkSubmissionResponse(
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
