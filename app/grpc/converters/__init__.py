# Converters - Per-entity conversion functions
# Server-side (model → proto)
from app.grpc.converters.employee import employee_to_proto, employee_info_to_proto
from app.grpc.converters.org_unit import org_unit_to_proto, org_unit_info_to_proto

# Client-side (proto → dict)
from app.grpc.converters.sso_user import (
    user_proto_to_dict,
    auth_user_proto_to_dict,
    session_proto_to_dict,
    login_response_to_dict,
)

__all__ = [
    # Server-side
    "employee_to_proto",
    "employee_info_to_proto",
    "org_unit_to_proto",
    "org_unit_info_to_proto",
    # Client-side
    "user_proto_to_dict",
    "auth_user_proto_to_dict",
    "session_proto_to_dict",
    "login_response_to_dict",
]
