"""
Employee Converters

Server-side: Convert Employee model to protobuf message.
"""

from proto.employee import employee_pb2
from app.grpc.utils import datetime_to_timestamp


def employee_to_proto(employee) -> employee_pb2.Employee:
    """Convert Employee model to protobuf message."""
    proto = employee_pb2.Employee(
        employee_id=employee.id,
        employee_number=employee.code or "",  # Map code to employee_number for proto compatibility
        employee_name=employee.name or (employee.user.name if employee.user else ""),
        employee_email=employee.email or (employee.user.email if employee.user else ""),
        employee_phone=employee.user.phone if employee.user else "",
        employee_position=employee.position or "",
        employee_type=employee.type or "",
        employee_gender=employee.user.gender if employee.user else "",
        employee_org_unit_id=employee.org_unit_id or 0,
        employee_supervisor_id=employee.supervisor_id or 0,
        is_active=employee.is_active,
        created_by=employee.created_by or 0,
        updated_by=employee.updated_by or 0,
    )
    
    # Set timestamps
    if employee.created_at:
        proto.created_at.CopyFrom(datetime_to_timestamp(employee.created_at))
    if employee.updated_at:
        proto.updated_at.CopyFrom(datetime_to_timestamp(employee.updated_at))
    if employee.deleted_at:
        proto.deleted_at.CopyFrom(datetime_to_timestamp(employee.deleted_at))
    if employee.deleted_by:
        proto.deleted_by = employee.deleted_by
    
    # Set org unit info
    if employee.org_unit:
        proto.org_unit.CopyFrom(employee_pb2.OrgUnitInfo(
            org_unit_id=employee.org_unit.id,
            org_unit_code=employee.org_unit.code or "",
            org_unit_name=employee.org_unit.name or "",
            org_unit_type=employee.org_unit.type or "",
        ))
    
    # Set supervisor info
    if employee.supervisor:
        supervisor_name = employee.supervisor.name
        if not supervisor_name and employee.supervisor.user:
            supervisor_name = employee.supervisor.user.name
        proto.supervisor.CopyFrom(employee_pb2.EmployeeInfo(
            employee_id=employee.supervisor.id,
            employee_number=employee.supervisor.code or "",
            employee_name=supervisor_name or "",
            employee_position=employee.supervisor.position or "",
        ))
    
    # Set metadata
    if employee.metadata_:
        proto.employee_metadata.update(employee.metadata_)
    
    return proto


def employee_info_to_proto(employee) -> employee_pb2.EmployeeInfo:
    """Convert Employee model to EmployeeInfo protobuf."""
    name = employee.name
    if not name and employee.user:
        name = employee.user.name
    return employee_pb2.EmployeeInfo(
        employee_id=employee.id,
        employee_number=employee.code or "",
        employee_name=name or "",
        employee_position=employee.position or "",
    )
