"""
Job untuk memproses assignment status transitions.

Business Logic:
- Berjalan setiap hari jam 00:30 WIB
- Activate pending assignments yang start_date sudah tercapai
- Expire active assignments yang end_date sudah terlewati
- Publish event untuk setiap transition
"""

from typing import Dict, Any
from datetime import date
import logging

from app.core.scheduler.base import BaseScheduledJob
from app.config.database import get_db_context
from app.modules.employee_assignments.repositories import (
    AssignmentQueries,
    AssignmentCommands,
)
from app.modules.employee_assignments.use_cases import (
    ActivateAssignmentUseCase,
    ExpireAssignmentUseCase,
)

logger = logging.getLogger(__name__)


class ProcessAssignmentsJob(BaseScheduledJob):
    """
    Job untuk memproses assignment status transitions.

    - Pending → Active: ketika start_date tercapai
    - Active → Expired: ketika end_date terlewati
    """

    job_id = "process_assignments"
    description = "Proses assignment status transitions (activate/expire)"
    cron = "30 0 * * *"  # Setiap hari jam 00:30 WIB
    enabled = True
    max_retries = 3

    async def execute(self) -> Dict[str, Any]:
        """
        Execute job: proses activate dan expire assignments.

        Returns:
            Dict dengan hasil eksekusi
        """
        today = date.today()

        activated_count = 0
        expired_count = 0
        error_count = 0

        logger.info(f"Memulai process assignments untuk tanggal: {today}")

        try:
            async with get_db_context() as db:
                queries = AssignmentQueries(db)
                commands = AssignmentCommands(db)

                activate_uc = ActivateAssignmentUseCase(queries, commands)
                expire_uc = ExpireAssignmentUseCase(queries, commands)

                # 1. Activate pending assignments
                pending_to_activate = await queries.get_pending_to_activate(today)
                logger.info(
                    f"Ditemukan {len(pending_to_activate)} assignment untuk diaktifkan"
                )

                for assignment in pending_to_activate:
                    try:
                        await activate_uc.execute(
                            assignment_id=assignment.id,
                            updated_by="system:scheduler",
                        )
                        activated_count += 1
                        logger.debug(f"Assignment {assignment.id} berhasil diaktifkan")
                    except Exception as e:
                        logger.error(f"Error activate assignment {assignment.id}: {e}")
                        error_count += 1

                # 2. Expire active assignments
                active_to_expire = await queries.get_active_to_expire(today)
                logger.info(
                    f"Ditemukan {len(active_to_expire)} assignment untuk di-expire"
                )

                for assignment in active_to_expire:
                    try:
                        await expire_uc.execute(
                            assignment_id=assignment.id,
                            updated_by="system:scheduler",
                        )
                        expired_count += 1
                        logger.debug(f"Assignment {assignment.id} berhasil di-expire")
                    except Exception as e:
                        logger.error(f"Error expire assignment {assignment.id}: {e}")
                        error_count += 1

                message = (
                    f"Process assignments selesai. "
                    f"Activated: {activated_count}, "
                    f"Expired: {expired_count}, "
                    f"Errors: {error_count}"
                )

                logger.info(message)

                return {
                    "success": True,
                    "message": message,
                    "data": {
                        "date": today.isoformat(),
                        "activated": activated_count,
                        "expired": expired_count,
                        "errors": error_count,
                    },
                }

        except Exception as e:
            error_message = f"Error saat execute process assignments: {str(e)}"
            logger.error(error_message, exc_info=True)
            raise Exception(error_message)
