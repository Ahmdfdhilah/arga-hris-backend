from typing import Optional, List, Dict, Any, Tuple
from datetime import date
from fastapi import UploadFile, HTTPException
from app.modules.work_submissions.repositories.work_submission_repository import (
    WorkSubmissionRepository,
)
from app.modules.work_submissions.schemas.requests import (
    WorkSubmissionCreateRequest,
    WorkSubmissionUpdateRequest,
)
from app.modules.work_submissions.schemas.responses import (
    WorkSubmissionResponse,
    WorkSubmissionListResponse,
)
from app.modules.work_submissions.schemas.shared import (
    FileMetadata,
    SubmissionStatus,
)
from app.core.exceptions.client_error import NotFoundException, ConflictException
from app.core.exceptions import ValidationException
from app.core.utils.file_upload import (
    upload_file_to_gcp,
    generate_signed_url_for_path,
    delete_file_from_gcp_url,
)
from app.core.utils.datetime import get_utc_now
from app.config.constants import FileUploadConstants
from app.config.settings import settings
from app.external_clients.grpc.employee_client import EmployeeGRPCClient


class WorkSubmissionService:
    """Service untuk business logic work submissions."""

    ALLOWED_FILE_TYPES = (
        FileUploadConstants.ALLOWED_DOCUMENT_TYPES
        | FileUploadConstants.ALLOWED_IMAGE_TYPES
        | {
            "application/vnd.ms-powerpoint",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/zip",
            "application/x-zip-compressed",
        }
    )
    MAX_FILE_SIZE = settings.MAX_DOCUMENT_SIZE
    MAX_FILES_PER_SUBMISSION = 10

    def __init__(
        self,
        work_submission_repo: WorkSubmissionRepository,
        employee_client: EmployeeGRPCClient,
    ):
        self.work_submission_repo = work_submission_repo
        self.employee_client = employee_client

    def _convert_files_paths_to_urls(
        self, files_metadata: List[Dict[str, Any]]
    ) -> List[FileMetadata]:
        """Convert file paths to signed URLs."""
        files_with_urls: List[FileMetadata] = []
        for file_meta in files_metadata:
            file_path = file_meta.get("file_path")
            file_name = file_meta.get("file_name")
            file_size = file_meta.get("file_size")
            file_path = file_meta.get("file_path")
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

    async def get_my_submissions(
        self,
        employee_id: int,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmissionResponse], Dict[str, Any]]:
        """Get work submissions milik employee sendiri."""
        skip = (page - 1) * limit

        submissions = await self.work_submission_repo.list_by_employee(
            employee_id=employee_id,
            submission_month=submission_month,
            status=status,
            skip=skip,
            limit=limit,
        )

        total = await self.work_submission_repo.count_by_employee(
            employee_id=employee_id,
            submission_month=submission_month,
            status=status,
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

        pagination = {
            "page": page,
            "limit": limit,
            "total_items": total,
        }
        return response_data, pagination

    async def create_submission(
        self,
        request: WorkSubmissionCreateRequest,
        created_by_user_id: int,
    ) -> WorkSubmissionResponse:
        """Create work submission baru."""
        normalized_month = date(
            request.submission_month.year, request.submission_month.month, 1
        )

        existing = await self.work_submission_repo.check_existing_submission(
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

        submission = await self.work_submission_repo.create(submission_data)

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

    async def get_submission_by_id(self, submission_id: int) -> WorkSubmissionResponse:
        """Get work submission by ID."""
        submission = await self.work_submission_repo.get(submission_id)

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

    async def update_submission(
        self,
        submission_id: int,
        request: WorkSubmissionUpdateRequest,
    ) -> WorkSubmissionResponse:
        """Update work submission."""
        submission = await self.work_submission_repo.get(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        # Validation: Cannot edit submission that is already submitted
        if submission.status == "submitted":
            raise ValidationException(
                "Submission yang sudah disubmit tidak dapat diedit lagi"
            )

        update_data: Dict[str, Any] = {}
        if request.title is not None:
            update_data["title"] = request.title
        if request.description is not None:
            update_data["description"] = request.description
        if request.status is not None:
            # Validation: When changing to submitted, must have at least 1 file
            if request.status.value == "submitted":
                files_count = len(submission.files or [])
                if files_count == 0:
                    raise ValidationException(
                        "Tidak dapat submit. Minimal 1 file harus diupload sebelum submit"
                    )

                if submission.status != "submitted":
                    update_data["submitted_at"] = get_utc_now()

            update_data["status"] = request.status.value

        updated_submission = await self.work_submission_repo.update(
            submission_id, update_data
        )

        if not updated_submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan setelah update"
            )

        files_with_urls = self._convert_files_paths_to_urls(
            updated_submission.files or []
        )

        return WorkSubmissionResponse(
            id=updated_submission.id,
            employee_id=updated_submission.employee_id,
            submission_month=updated_submission.submission_month,
            title=updated_submission.title,
            description=updated_submission.description,
            files=files_with_urls,
            status=SubmissionStatus(updated_submission.status),
            submitted_at=updated_submission.submitted_at,
            created_by=updated_submission.created_by,
            created_at=updated_submission.created_at,
            updated_at=updated_submission.updated_at,
        )

    async def delete_submission(self, submission_id: int) -> None:
        """Delete work submission dan semua files-nya."""
        submission = await self.work_submission_repo.get(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        for file_meta in submission.files or []:
            file_path = file_meta.get("file_path")
            if file_path:
                signed_url = generate_signed_url_for_path(file_path)
                if signed_url:
                    delete_file_from_gcp_url(signed_url)

        await self.work_submission_repo.delete(submission_id)

    async def upload_files(
        self,
        submission_id: int,
        files: List[UploadFile],
    ) -> WorkSubmissionResponse:
        """Upload files ke submission yang sudah ada."""
        submission = await self.work_submission_repo.get(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        # Validation: Cannot upload files to submitted submission
        if submission.status == "submitted":
            raise ValidationException(
                "Tidak dapat upload file. Submission yang sudah disubmit tidak dapat diedit lagi"
            )

        current_files_count = len(submission.files or [])
        if current_files_count + len(files) > self.MAX_FILES_PER_SUBMISSION:
            raise HTTPException(
                status_code=400,
                detail=f"Maksimal {self.MAX_FILES_PER_SUBMISSION} files per submission. "
                f"Saat ini ada {current_files_count} files.",
            )

        uploaded_files_metadata: List[Dict[str, Any]] = []
        for file in files:
            _, file_path = await upload_file_to_gcp(
                file=file,
                entity_type="work_submissions",
                entity_id=submission.employee_id,
                subfolder=f"{submission.submission_month.year}/{submission.submission_month.month}/{submission_id}",
                allowed_types=self.ALLOWED_FILE_TYPES,
                max_size=self.MAX_FILE_SIZE,
            )

            content = await file.read()
            file_size = len(content)
            await file.seek(0)

            if file.filename is None or file.content_type is None:
                raise HTTPException(
                    status_code=400,
                    detail="File harus memiliki nama dan content type",
                )

            file_metadata = FileMetadata(
                file_name=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file.content_type,
                file_url=None,
            )
            uploaded_files_metadata.append(file_metadata.model_dump())

        current_files: List[Dict[str, Any]] = submission.files or []
        updated_files = current_files + uploaded_files_metadata

        await self.work_submission_repo.update(submission_id, {"files": updated_files})

        updated_submission = await self.work_submission_repo.get(submission_id)

        if not updated_submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan setelah upload"
            )

        files_with_urls = self._convert_files_paths_to_urls(
            updated_submission.files or []
        )

        return WorkSubmissionResponse(
            id=updated_submission.id,
            employee_id=updated_submission.employee_id,
            submission_month=updated_submission.submission_month,
            title=updated_submission.title,
            description=updated_submission.description,
            files=files_with_urls,
            status=SubmissionStatus(updated_submission.status),
            submitted_at=updated_submission.submitted_at,
            created_by=updated_submission.created_by,
            created_at=updated_submission.created_at,
            updated_at=updated_submission.updated_at,
        )

    async def delete_file(
        self,
        submission_id: int,
        file_path: str,
    ) -> WorkSubmissionResponse:
        """Delete single file dari submission."""
        submission = await self.work_submission_repo.get(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        # Validation: Cannot delete files from submitted submission
        if submission.status == "submitted":
            raise ValidationException(
                "Tidak dapat hapus file. Submission yang sudah disubmit tidak dapat diedit lagi"
            )

        current_files: List[Dict[str, Any]] = submission.files or []
        file_found = False
        updated_files: List[Dict[str, Any]] = []

        for file_meta in current_files:
            if file_meta.get("file_path") == file_path:
                file_found = True
                signed_url = generate_signed_url_for_path(file_path)
                if signed_url:
                    delete_file_from_gcp_url(signed_url)
            else:
                updated_files.append(file_meta)

        if not file_found:
            raise NotFoundException(f"File dengan path {file_path} tidak ditemukan")

        await self.work_submission_repo.update(submission_id, {"files": updated_files})

        updated_submission = await self.work_submission_repo.get(submission_id)

        if not updated_submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan setelah delete file"
            )

        files_with_urls = self._convert_files_paths_to_urls(
            updated_submission.files or []
        )

        return WorkSubmissionResponse(
            id=updated_submission.id,
            employee_id=updated_submission.employee_id,
            submission_month=updated_submission.submission_month,
            title=updated_submission.title,
            description=updated_submission.description,
            files=files_with_urls,
            status=SubmissionStatus(updated_submission.status),
            submitted_at=updated_submission.submitted_at,
            created_by=updated_submission.created_by,
            created_at=updated_submission.created_at,
            updated_at=updated_submission.updated_at,
        )

    async def list_all_submissions(
        self,
        employee_id: Optional[int] = None,
        submission_month: Optional[date] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[WorkSubmissionListResponse], Dict[str, Any]]:
        """List semua submissions untuk admin."""
        skip = (page - 1) * limit

        submissions = await self.work_submission_repo.list_all_submissions(
            employee_id=employee_id,
            submission_month=submission_month,
            status=status,
            skip=skip,
            limit=limit,
        )

        total = await self.work_submission_repo.count_all_submissions(
            employee_id=employee_id,
            submission_month=submission_month,
            status=status,
        )

        response_data: List[WorkSubmissionListResponse] = []
        for submission in submissions:
            employee_name: Optional[str] = None
            employee_number: Optional[str] = None
            try:
                employee_info = await self.employee_client.get_employee(
                    submission.employee_id
                )
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

        pagination = {
            "page": page,
            "limit": limit,
            "total_items": total,
        }
        return response_data, pagination
