"""
OrgUnit Converters

Server-side: Convert OrgUnit model to protobuf message.
"""

from proto.org_unit import org_unit_pb2
from app.grpc.utils import datetime_to_timestamp


def org_unit_to_proto(org_unit) -> org_unit_pb2.OrgUnit:
    """Convert OrgUnit model to protobuf message."""
    proto = org_unit_pb2.OrgUnit(
        org_unit_id=org_unit.id,
        org_unit_code=org_unit.code or "",
        org_unit_name=org_unit.name or "",
        org_unit_type=org_unit.type or "",
        org_unit_parent_id=org_unit.parent_id or 0,
        org_unit_level=org_unit.level or 0,
        org_unit_path=org_unit.path or "",
        org_unit_head_id=org_unit.head_id or 0,
        org_unit_description=org_unit.description or "",
        is_active=org_unit.is_active,
        created_by=org_unit.created_by or 0,
        updated_by=org_unit.updated_by or 0,
        employee_count=org_unit.employee_count if hasattr(org_unit, 'employee_count') else 0,
        total_employee_count=org_unit.total_employee_count if hasattr(org_unit, 'total_employee_count') else 0,
    )
    
    # Set timestamps
    if org_unit.created_at:
        proto.created_at.CopyFrom(datetime_to_timestamp(org_unit.created_at))
    if org_unit.updated_at:
        proto.updated_at.CopyFrom(datetime_to_timestamp(org_unit.updated_at))
    if org_unit.deleted_at:
        proto.deleted_at.CopyFrom(datetime_to_timestamp(org_unit.deleted_at))
    if org_unit.deleted_by:
        proto.deleted_by = org_unit.deleted_by
    
    # Set parent info
    if org_unit.parent:
        proto.parent.CopyFrom(org_unit_pb2.OrgUnitInfo(
            org_unit_id=org_unit.parent.id,
            org_unit_code=org_unit.parent.code or "",
            org_unit_name=org_unit.parent.name or "",
            org_unit_type=org_unit.parent.type or "",
        ))
    
    # Set head info
    if org_unit.head:
        proto.head.CopyFrom(org_unit_pb2.EmployeeInfo(
            employee_id=org_unit.head.id,
            employee_number=org_unit.head.number or "",
            employee_name=org_unit.head.user.name if org_unit.head.user else "",
            employee_position=org_unit.head.position or "",
        ))
    
    # Set metadata
    if org_unit.metadata:
        proto.org_unit_metadata.update(org_unit.metadata)
    
    return proto


def org_unit_info_to_proto(org_unit) -> org_unit_pb2.OrgUnitInfo:
    """Convert OrgUnit model to OrgUnitInfo protobuf."""
    return org_unit_pb2.OrgUnitInfo(
        org_unit_id=org_unit.id,
        org_unit_code=org_unit.code or "",
        org_unit_name=org_unit.name or "",
        org_unit_type=org_unit.type or "",
    )
