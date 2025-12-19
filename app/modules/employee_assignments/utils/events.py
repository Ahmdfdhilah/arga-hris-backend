"""
Event helper functions untuk Employee Assignments module.
"""

from typing import Dict, Any
from app.modules.employee_assignments.models.employee_assignment import (
    EmployeeAssignment,
)


def build_assignment_event_data(assignment: EmployeeAssignment) -> Dict[str, Any]:
    """
    Build event data payload dari EmployeeAssignment model.

    Returns:
        Dict dengan semua field yang diperlukan consumer services.
    """
    return {
        "id": assignment.id,
        "employee_id": assignment.employee_id,
        "replaced_employee_id": assignment.replaced_employee_id,
        "org_unit_id": assignment.org_unit_id,
        "status": assignment.status,
        "start_date": assignment.start_date.isoformat()
        if assignment.start_date
        else None,
        "end_date": assignment.end_date.isoformat() if assignment.end_date else None,
        "leave_request_id": assignment.leave_request_id,
        "reason": assignment.reason,
    }
