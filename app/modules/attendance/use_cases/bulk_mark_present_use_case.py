from app.modules.attendance.repositories import AttendanceQueries, AttendanceCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.attendance.schemas import (
    BulkMarkPresentRequest,
    BulkMarkPresentSummary,
)


class BulkMarkPresentUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        commands: AttendanceCommands,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.commands = commands
        self.employee_queries = employee_queries

    async def execute(
        self,
        request: BulkMarkPresentRequest,
        created_by: str,
    ) -> BulkMarkPresentSummary:
        # Get all active employees
        all_employees = []
        page = 1
        limit = 200

        while True:
            skip = (page - 1) * limit
            employees, total = await self.employee_queries.list(
                is_active=True, limit=limit, skip=skip
            )

            if not employees:
                break

            all_employees.extend(employees)

            total_pages = (total + limit - 1) // limit if total > 0 else 0
            if page >= total_pages:
                break
            page += 1

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for employee in all_employees:
            try:
                # Check existing
                existing = await self.queries.get_by_employee_and_date(
                    employee.id, request.attendance_date
                )

                if existing:
                    update_data = {
                        "status": "present",
                        "check_in_notes": request.notes,
                    }
                    await self.commands.update(existing.id, update_data)
                    updated_count += 1
                else:
                    attendance_data = {
                        "employee_id": employee.id,
                        "org_unit_id": employee.org_unit_id,
                        "attendance_date": request.attendance_date,
                        "status": "present",
                        "check_in_notes": request.notes,
                        "created_by": created_by,
                    }
                    await self.commands.create(attendance_data)
                    created_count += 1
            except Exception as e:
                print(f"Error processing employee {employee.id}: {str(e)}")
                skipped_count += 1
                continue

        return BulkMarkPresentSummary(
            total_employees=len(all_employees),
            created=created_count,
            updated=updated_count,
            skipped=skipped_count,
            attendance_date=request.attendance_date.strftime("%Y-%m-%d"),
            notes=request.notes,
        )
