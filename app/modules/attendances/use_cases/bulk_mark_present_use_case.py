import uuid
from app.modules.attendances.repositories import AttendanceQueries, AttendanceCommands
from app.modules.employees.repositories import EmployeeQueries
from app.modules.attendances.schemas import (
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
        created_by: "uuid.UUID",
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

        employee_data_list = [
            {"id": e.id, "org_unit_id": e.org_unit_id} for e in all_employees
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for emp_data in employee_data_list:
            emp_id = emp_data["id"]
            org_id = emp_data["org_unit_id"]
            try:
                # Check existing
                existing = await self.queries.get_by_employee_and_date(
                    emp_id, request.attendance_date
                )

                if existing:
                    existing.status = "present"
                    existing.check_in_notes = request.notes
                    existing.updated_by = created_by
                    await self.commands.update(existing)
                    updated_count += 1
                else:
                    from app.modules.attendances.models.attendances import Attendance

                    attendance = Attendance(
                        employee_id=emp_id,
                        org_unit_id=org_id,
                        attendance_date=request.attendance_date,
                        status="present",
                        check_in_notes=request.notes,
                        created_by=created_by,
                    )
                    await self.commands.create(attendance)
                    created_count += 1
            except Exception as e:
                await self.queries.db.rollback()
                print(f"Error processing employee {emp_id}: {str(e)}")
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
