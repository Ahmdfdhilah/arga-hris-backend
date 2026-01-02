"""
Attendance Leave Sync Utility

Synchronizes attendance status with leave requests.
This module uses only repositories to avoid circular dependencies.
"""

from datetime import date, timedelta
from typing import Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendances.models.attendances import Attendance
from app.modules.attendances.repositories import AttendanceQueries, AttendanceCommands


logger = logging.getLogger(__name__)


async def sync_attendances_to_leave(
    db: AsyncSession,
    employee_id: int,
    start_date: date,
    end_date: date,
    org_unit_id: Optional[int] = None,
) -> int:
    """
    Update attendance records in the date range to status='leave'.
    Creates attendance records if they don't exist.
    
    Args:
        db: Database session
        employee_id: Employee to sync attendances for
        start_date: Start of leave period
        end_date: End of leave period
        org_unit_id: Optional org unit ID for new attendance records
    
    Returns:
        Number of attendance records updated/created
    """
    queries = AttendanceQueries(db)
    commands = AttendanceCommands(db)
    
    synced_count = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Skip weekends (Sunday = 6)
        if current_date.weekday() != 6:
            attendance = await queries.get_by_employee_and_date(
                employee_id=employee_id,
                attendance_date=current_date,
            )
            
            if attendance:
                # Update existing attendance to 'leave'
                if attendance.status != "leave":
                    attendance.status = "leave"
                    await commands.update(attendance)
                    synced_count += 1
                    logger.debug(
                        f"Updated attendance for employee_id={employee_id}, "
                        f"date={current_date} to status='leave'"
                    )
            else:
                # Create new attendance with status='leave'
                new_attendance = Attendance(
                    employee_id=employee_id,
                    org_unit_id=org_unit_id,
                    attendance_date=current_date,
                    status="leave",
                )
                await commands.create(new_attendance)
                synced_count += 1
                logger.debug(
                    f"Created attendance for employee_id={employee_id}, "
                    f"date={current_date} with status='leave'"
                )
        
        current_date += timedelta(days=1)
    
    logger.info(
        f"Synced {synced_count} attendance records to 'leave' for "
        f"employee_id={employee_id}, range={start_date} to {end_date}"
    )
    
    return synced_count


async def revert_attendances_from_leave(
    db: AsyncSession,
    employee_id: int,
    start_date: date,
    end_date: date,
) -> int:
    """
    Revert attendance records from 'leave' to 'absent' when leave is deleted.
    Only reverts records that have status='leave' and no check-in/check-out.
    
    Args:
        db: Database session
        employee_id: Employee to revert attendances for
        start_date: Start of leave period
        end_date: End of leave period
    
    Returns:
        Number of attendance records reverted
    """
    queries = AttendanceQueries(db)
    commands = AttendanceCommands(db)
    
    reverted_count = 0
    current_date = start_date
    
    while current_date <= end_date:
        attendance = await queries.get_by_employee_and_date(
            employee_id=employee_id,
            attendance_date=current_date,
        )
        
        if attendance and attendance.status == "leave":
            # Only revert if no actual check-in/check-out data
            if not attendance.check_in_time and not attendance.check_out_time:
                attendance.status = "absent"
                await commands.update(attendance)
                reverted_count += 1
                logger.debug(
                    f"Reverted attendance for employee_id={employee_id}, "
                    f"date={current_date} from 'leave' to 'absent'"
                )
        
        current_date += timedelta(days=1)
    
    logger.info(
        f"Reverted {reverted_count} attendance records from 'leave' for "
        f"employee_id={employee_id}, range={start_date} to {end_date}"
    )
    
    return reverted_count


async def check_employee_has_leave(
    db: AsyncSession,
    employee_id: int,
    check_date: date,
) -> bool:
    """
    Check if an employee has an active leave request for a given date.
    
    Args:
        db: Database session
        employee_id: Employee to check
        check_date: Date to check for leave
    
    Returns:
        True if employee has leave on this date
    """
    from app.modules.leave_requests.repositories import LeaveRequestQueries
    
    leave_queries = LeaveRequestQueries(db)
    leave_request = await leave_queries.is_on_leave(
        employee_id=employee_id,
        check_date=check_date,
    )
    
    return leave_request is not None
