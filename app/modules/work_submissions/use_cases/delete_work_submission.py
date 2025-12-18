from app.modules.work_submissions.repositories import (
    WorkSubmissionQueries,
    WorkSubmissionCommands,
)
from app.core.exceptions.client_error import NotFoundException
from app.core.utils.file_upload import (
    generate_signed_url_for_path,
    delete_file_from_gcp_url,
)


class DeleteWorkSubmissionUseCase:
    def __init__(
        self,
        queries: WorkSubmissionQueries,
        commands: WorkSubmissionCommands,
    ):
        self.queries = queries
        self.commands = commands

    async def execute(self, submission_id: int) -> None:
        submission = await self.queries.get_by_id(submission_id)

        if not submission:
            raise NotFoundException(
                f"Work submission dengan ID {submission_id} tidak ditemukan"
            )

        # Optional: Prevent deleting submitted work?
        # Original service didn't have this check on delete_submission, but consistent with others?
        # Let's keep original behavior (allow delete) or add it if logical.
        # Original code: lines 286-303 NO status check. So we keep it allowed.

        for file_meta in submission.files or []:
            file_path = file_meta.get("file_path")
            if file_path:
                signed_url = generate_signed_url_for_path(file_path)
                if signed_url:
                    delete_file_from_gcp_url(signed_url)

        await self.commands.delete(submission_id)
