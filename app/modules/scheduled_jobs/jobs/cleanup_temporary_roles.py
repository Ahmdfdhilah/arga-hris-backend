"""
Job untuk cleanup expired temporary user roles.

Business Logic:
- Berjalan setiap hari jam 01:00 WIB
- Menghapus user_roles dengan is_temporary=True yang valid_until < now
"""

from typing import Dict, Any
import logging

from sqlalchemy import delete, and_

from app.core.scheduler.base import BaseScheduledJob
from app.config.database import get_db_context
from app.modules.users.rbac.models.user_role import UserRole
from app.core.utils.datetime import get_utc_now

logger = logging.getLogger(__name__)


class CleanupTemporaryRolesJob(BaseScheduledJob):
    """
    Job untuk menghapus temporary roles yang sudah expired.
    """

    job_id = "cleanup_temporary_roles"
    description = "Cleanup expired temporary user roles"
    cron = "0 1 * * *"  # Setiap hari jam 01:00 WIB
    enabled = True
    max_retries = 3

    async def execute(self) -> Dict[str, Any]:
        """
        Execute job: hapus temporary roles yang expired.

        Returns:
            Dict dengan hasil eksekusi
        """
        now = get_utc_now()
        deleted_count = 0

        logger.info(f"Memulai cleanup temporary roles untuk waktu: {now}")

        try:
            async with get_db_context() as db:
                # Delete expired temporary roles
                stmt = delete(UserRole).where(
                    and_(
                        UserRole.is_temporary == True,  # noqa: E712
                        UserRole.valid_until < now,
                    )
                )

                result = await db.execute(stmt)
                deleted_count = result.rowcount
                await db.commit()

                message = f"Cleanup temporary roles selesai. Deleted: {deleted_count}"
                logger.info(message)

                return {
                    "success": True,
                    "message": message,
                    "data": {
                        "timestamp": now.isoformat(),
                        "deleted_count": deleted_count,
                    },
                }

        except Exception as e:
            error_message = f"Error saat cleanup temporary roles: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise Exception(error_message)
