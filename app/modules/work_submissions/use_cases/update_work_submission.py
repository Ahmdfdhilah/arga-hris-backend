from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from app.modules.work_submissions.schemas.requests import WorkSubmissionUpdateRequest
from app.modules.work_submissions.schemas.responses import WorkSubmissionResponse
from app.modules.work_submissions.schemas.shared import SubmissionStatus, FileMetadata
from app.modules.work_submissions.repositories import (
    WorkSubmissionQueries,
    WorkSubmissionCommands,
)
from app.core.exceptions.client_error import (
    NotFoundException,
    UnprocessableEntityException,
)
from app.core.utils.file_upload import (
    upload_file_to_gcp,
    generate_signed_url_for_path,
    delete_file_from_gcp_url,
)
from app.core.utils.datetime import get_utc_now
from app.config.constants import FileUploadConstants
from app.config.settings import settings


class UpdateWorkSubmissionUseCase:
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
        queries: WorkSubmissionQueries,
        commands: WorkSubmissionCommands,
    ):
        self.queries = queries
        self.commands = commands

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

    async def execute_update(
        self, submission_id: int, request: WorkSubmissionUpdateRequest
    ) -> WorkSubmissionResponse:
        submission = await self.queries.get_by_id(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        if submission.status == "submitted":
            raise UnprocessableEntityException(
                "Submission yang sudah disubmit tidak dapat diedit lagi"
            )

        update_data: Dict[str, Any] = {}
        if request.title is not None:
            update_data["title"] = request.title
        if request.description is not None:
            update_data["description"] = request.description
        if request.status is not None:
            if request.status.value == "submitted":
                files_count = len(submission.files or [])
                if files_count == 0:
                    raise UnprocessableEntityException(
                        "Tidak dapat submit. Minimal 1 file harus diupload sebelum submit"
                    )

                if submission.status != "submitted":
                    update_data["submitted_at"] = get_utc_now()

            update_data["status"] = request.status.value

        updated_submission = await self.commands.update(submission_id, update_data)

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

    async def upload_files(
        self, submission_id: int, files: List[UploadFile]
    ) -> WorkSubmissionResponse:
        submission = await self.queries.get_by_id(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        if submission.status == "submitted":
            raise UnprocessableEntityException(
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

        await self.commands.update(submission_id, {"files": updated_files})

        updated_submission = await self.queries.get_by_id(submission_id)

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
        self, submission_id: int, file_path: str
    ) -> WorkSubmissionResponse:
        submission = await self.queries.get_by_id(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        if submission.status == "submitted":
            raise UnprocessableEntityException(
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

        await self.commands.update(submission_id, {"files": updated_files})

        updated_submission = await self.queries.get_by_id(submission_id)

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
