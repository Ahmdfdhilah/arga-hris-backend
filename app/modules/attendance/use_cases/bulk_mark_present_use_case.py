from app.modules.attendance.repositories import AttendanceQueries, AttendanceCommands
from app.modules.employees.repositories import (
    EmployeeQueries,
    EmployeeFilters,
    PaginationParams,
)
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
            params = PaginationParams(page=page, limit=limit)
            filters = EmployeeFilters(is_active=True)
            employees, pagination = await self.employee_queries.list(params, filters)

            all_employees.extend(employees)

            if page >= pagination.total_pages:
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
                # Log error? using print as in original code for now
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
