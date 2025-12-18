from typing import List
from datetime import date
from decimal import Decimal
from app.modules.attendance.repositories import AttendanceQueries
from app.modules.employees.repositories import (
    EmployeeQueries,
    EmployeeFilters,
    PaginationParams,
)
from app.modules.attendance.schemas import (
    EmployeeAttendanceReport,
    AttendanceRecordInReport,
)
from app.modules.attendance.schemas.shared import AttendanceStatus
from app.core.exceptions.client_error import BadRequestException
from app.core.utils.workforce import (
    generate_working_days_list as generate_working_days_for_employee,
)


class GetAttendanceReportUseCase:
    def __init__(
        self,
        queries: AttendanceQueries,
        employee_queries: EmployeeQueries,
    ):
        self.queries = queries
        self.employee_queries = employee_queries

    async def execute(
        self,
        org_unit_id: int,
        start_date: date,
        end_date: date,
    ) -> List[EmployeeAttendanceReport]:
        if start_date > end_date:
            raise BadRequestException(
                "Tanggal mulai tidak boleh lebih besar dari tanggal akhir"
            )

        # Get all employees from org unit (pagination loop)
        all_employees = []
        page = 1
        limit = 200

        while True:
            params = PaginationParams(page=page, limit=limit)
            filters = EmployeeFilters(org_unit_id=org_unit_id, is_active=True)
            employees, pagination = await self.employee_queries.list(
                params, filters
            )  # Assuming list supports org_unit_id

            all_employees.extend(employees)

            if page >= pagination.total_pages:
                break
            page += 1

        if not all_employees:
            return []

        attendances = await self.queries.get_report_by_org_unit(
            org_unit_id=org_unit_id,
            start_date=start_date,
            end_date=end_date,
        )

        attendance_by_employee_date = {}
        for att in attendances:
            if att.employee_id not in attendance_by_employee_date:
                attendance_by_employee_date[att.employee_id] = {}
            attendance_by_employee_date[att.employee_id][att.attendance_date] = att

        report_data = []
        for employee in all_employees:
            # Generate working days
            employee_working_days = generate_working_days_for_employee(
                start_date, end_date, employee.employee_type
            )

            employee_att_dict = attendance_by_employee_date.get(employee.id, {})

            employee_attendances = []
            total_present_days = 0
            total_work_hours = 0.0
            total_overtime_hours = 0.0

            for working_day in employee_working_days:
                if working_day in employee_att_dict:
                    att = employee_att_dict[working_day]
                    record = AttendanceRecordInReport(
                        attendance_date=att.attendance_date,
                        status=att.status,
                        check_in_time=att.check_in_time,
                        check_out_time=att.check_out_time,
                        work_hours=att.work_hours,
                        overtime_hours=att.overtime_hours,
                    )

                    if att.status in ["present", "hybrid"]:
                        total_present_days += 1
                    if att.work_hours:
                        total_work_hours += float(att.work_hours)
                    if att.overtime_hours:
                        total_overtime_hours += float(att.overtime_hours)
                else:
                    record = AttendanceRecordInReport(
                        attendance_date=working_day,
                        status=AttendanceStatus.ABSENT,
                        check_in_time=None,
                        check_out_time=None,
                        work_hours=None,
                        overtime_hours=None,
                    )
                employee_attendances.append(record)

            org_unit_name = employee.org_unit.name if employee.org_unit else None

            employee_report = EmployeeAttendanceReport(
                employee_id=employee.id,
                employee_name=employee.user.name if employee.user else None,
                employee_number=employee.employee_number,
                employee_position=employee.position,
                employee_type=employee.employee_type,
                org_unit_id=employee.org_unit_id,
                org_unit_name=org_unit_name,
                attendances=employee_attendances,
                total_present_days=total_present_days,
                total_work_hours=(
                    Decimal(str(total_work_hours)) if total_work_hours else None
                ),
                total_overtime_hours=(
                    Decimal(str(total_overtime_hours)) if total_overtime_hours else None
                ),
            )
            report_data.append(employee_report)

        return report_data
