"""
gRPC Converters for HRIS Backend (Client-side)

Functions to convert between protobuf messages and dicts.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from proto.sso import user_pb2, auth_pb2


def user_proto_to_dict(user: user_pb2.User) -> Dict[str, Any]:
    """Convert gRPC User message to dict."""
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email or None,
        "phone": user.phone or None,
        "avatar_path": user.avatar_path or None,
        "status": user.status,
        "role": user.role,
        "alias": user.alias or None,
        "gender": user.gender or None,
        "date_of_birth": user.date_of_birth.ToDatetime() if user.HasField("date_of_birth") else None,
        "address": user.address or None,
        "bio": user.bio or None,
        "created_at": user.created_at.ToDatetime() if user.HasField("created_at") else None,
        "updated_at": user.updated_at.ToDatetime() if user.HasField("updated_at") else None,
    }


def auth_user_proto_to_dict(user: auth_pb2.UserData) -> Dict[str, Any]:
    """Convert gRPC auth UserData message to dict."""
    return {
        "id": user.id,
        "role": user.role,
        "name": user.name,
        "email": user.email,
        "avatar_url": user.avatar_url or None,
        "allowed_apps": [
            {"id": app.id, "code": app.code, "name": app.name}
            for app in user.allowed_apps
        ],
    }


def session_proto_to_dict(session: auth_pb2.SessionInfo) -> Dict[str, Any]:
    """Convert gRPC SessionInfo message to dict."""
    return {
        "device_id": session.device_id,
        "client_id": session.client_id,
        "ip_address": session.ip_address,
        "device_info": dict(session.device_info.extra) if session.HasField("device_info") else None,
        "created_at": session.created_at.ToDatetime() if session.HasField("created_at") else None,
        "last_activity": session.last_activity.ToDatetime() if session.HasField("last_activity") else None,
    }


def login_response_to_dict(response: auth_pb2.LoginResponse) -> Dict[str, Any]:
    """Convert gRPC LoginResponse to dict."""
    return {
        "success": response.success,
        "error": response.error if response.HasField("error") else None,
        "sso_token": response.sso_token or None,
        "access_token": response.access_token or None,
        "refresh_token": response.refresh_token or None,
        "token_type": response.token_type,
        "expires_in": response.expires_in if response.HasField("expires_in") else None,
        "user": auth_user_proto_to_dict(response.user) if response.HasField("user") else None,
    }
