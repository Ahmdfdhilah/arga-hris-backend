import grpc
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.external_clients.grpc.base_client import BaseGRPCClient
from app.config.settings import settings
from proto.sso import user_pb2, user_pb2_grpc, auth_pb2, auth_pb2_grpc


class SSOUserGRPCClient(BaseGRPCClient):
    """gRPC client for SSO UserService."""

    def __init__(self):
        super().__init__("SSOUserService")
        self.address = settings.sso_grpc_address

    async def get_stub(self) -> user_pb2_grpc.UserServiceStub:
        channel = await self.get_channel()
        return user_pb2_grpc.UserServiceStub(channel)

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from SSO."""
        try:
            stub = await self.get_stub()
            request = user_pb2.GetUserRequest(user_id=user_id)
            response = await stub.GetUser(request)
            
            if not response.found:
                return None
            
            return self._user_to_dict(response.user)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            await self.handle_grpc_error(e)

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from SSO."""
        try:
            stub = await self.get_stub()
            request = user_pb2.GetUserByEmailRequest(email=email)
            response = await stub.GetUserByEmail(request)
            
            if not response.found:
                return None
            
            return self._user_to_dict(response.user)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            await self.handle_grpc_error(e)

    async def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        """Get user by phone from SSO."""
        try:
            stub = await self.get_stub()
            request = user_pb2.GetUserByPhoneRequest(phone=phone)
            response = await stub.GetUserByPhone(request)
            
            if not response.found:
                return None
            
            return self._user_to_dict(response.user)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            await self.handle_grpc_error(e)

    async def batch_get_users(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """Batch get users by IDs from SSO."""
        try:
            stub = await self.get_stub()
            request = user_pb2.BatchGetUsersRequest(user_ids=user_ids)
            response = await stub.BatchGetUsers(request)
            
            return [self._user_to_dict(user) for user in response.users]
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    def _user_to_dict(self, user: user_pb2.User) -> Dict[str, Any]:
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

    async def create_user(
        self,
        email: str,
        name: str,
        role: str = "user",
        phone: Optional[str] = None,
        password: Optional[str] = None,
        alias: Optional[str] = None,
        gender: Optional[str] = None,
        address: Optional[str] = None,
        bio: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create user in SSO."""
        try:
            stub = await self.get_stub()
            request = user_pb2.CreateUserRequest(
                email=email,
                name=name,
                role=role,
                phone=phone or "",
                password=password or "",
                alias=alias or "",
                gender=gender or "",
                address=address or "",
                bio=bio or "",
            )
            response = await stub.CreateUser(request)
            
            return {
                "success": response.success,
                "error": response.error if response.HasField("error") else None,
                "user": self._user_to_dict(response.user) if response.HasField("user") else None,
                "temporary_password": response.temporary_password if response.HasField("temporary_password") else None,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        alias: Optional[str] = None,
        gender: Optional[str] = None,
        address: Optional[str] = None,
        bio: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update user in SSO."""
        try:
            stub = await self.get_stub()
            request = user_pb2.UpdateUserRequest(
                user_id=user_id,
                name=name or "",
                email=email or "",
                phone=phone or "",
                role=role or "",
                status=status or "",
                alias=alias or "",
                gender=gender or "",
                address=address or "",
                bio=bio or "",
            )
            response = await stub.UpdateUser(request)
            
            return {
                "success": response.success,
                "error": response.error if response.HasField("error") else None,
                "user": self._user_to_dict(response.user) if response.HasField("user") else None,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Soft delete user in SSO."""
        try:
            stub = await self.get_stub()
            request = user_pb2.DeleteUserRequest(user_id=user_id)
            response = await stub.DeleteUser(request)
            
            return {
                "success": response.success,
                "error": response.error if response.HasField("error") else None,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)


class SSOAuthGRPCClient(BaseGRPCClient):
    """gRPC client for SSO AuthService."""

    def __init__(self):
        super().__init__("SSOAuthService")
        self.address = settings.sso_grpc_address

    async def get_stub(self) -> auth_pb2_grpc.AuthServiceStub:
        channel = await self.get_channel()
        return auth_pb2_grpc.AuthServiceStub(channel)

    async def validate_token(self, access_token: str) -> Dict[str, Any]:
        """Validate access token and get user data."""
        try:
            stub = await self.get_stub()
            request = auth_pb2.ValidateTokenRequest(access_token=access_token)
            response = await stub.ValidateToken(request)
            
            return {
                "is_valid": response.is_valid,
                "user": self._user_data_to_dict(response.user) if response.HasField("user") else None,
                "error": response.error if response.HasField("error") else None,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def login_with_email(
        self,
        email: str,
        password: str,
        client_id: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        fcm_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Login with email/password via SSO."""
        try:
            stub = await self.get_stub()
            
            proto_device_info = None
            if device_info:
                proto_device_info = auth_pb2.DeviceInfo(
                    platform=device_info.get("platform", ""),
                    device_name=device_info.get("device_name", ""),
                    os_version=device_info.get("os_version", ""),
                    app_version=device_info.get("app_version", ""),
                )
            
            request = auth_pb2.EmailLoginRequest(
                email=email,
                password=password,
                client_id=client_id or "",
                device_info=proto_device_info,
                ip_address=ip_address or "",
                fcm_token=fcm_token or "",
            )
            response = await stub.LoginWithEmail(request)
            
            return self._login_response_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def refresh_token(
        self,
        refresh_token: str,
        device_id: str,
    ) -> Dict[str, Any]:
        """Refresh access token via SSO."""
        try:
            stub = await self.get_stub()
            request = auth_pb2.RefreshTokenRequest(
                refresh_token=refresh_token,
                device_id=device_id,
            )
            response = await stub.RefreshToken(request)
            
            return {
                "success": response.success,
                "error": response.error if response.HasField("error") else None,
                "access_token": response.access_token or None,
                "refresh_token": response.refresh_token or None,
                "token_type": response.token_type,
                "expires_in": response.expires_in if response.HasField("expires_in") else None,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def exchange_sso_token(
        self,
        sso_token: str,
        client_id: str,
        device_info: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        fcm_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Exchange SSO token for app-specific tokens."""
        try:
            stub = await self.get_stub()
            
            proto_device_info = None
            if device_info:
                proto_device_info = auth_pb2.DeviceInfo(
                    platform=device_info.get("platform", ""),
                    device_name=device_info.get("device_name", ""),
                    os_version=device_info.get("os_version", ""),
                    app_version=device_info.get("app_version", ""),
                )
            
            request = auth_pb2.SSOExchangeRequest(
                sso_token=sso_token,
                client_id=client_id,
                device_info=proto_device_info,
                ip_address=ip_address or "",
                fcm_token=fcm_token or "",
            )
            response = await stub.ExchangeSSOToken(request)
            
            return self._login_response_to_dict(response)
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def logout(
        self,
        user_id: str,
        client_id: Optional[str] = None,
        device_id: Optional[str] = None,
        global_logout: bool = False,
    ) -> Dict[str, Any]:
        """Logout user via SSO."""
        try:
            stub = await self.get_stub()
            request = auth_pb2.LogoutRequest(
                user_id=user_id,
                client_id=client_id or "",
                device_id=device_id or "",
                **{"global": global_logout},  # 'global' is a reserved keyword
            )
            response = await stub.Logout(request)
            
            return {
                "success": response.success,
                "error": response.error if response.HasField("error") else None,
                "message": response.message,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    async def get_sessions(self, user_id: str) -> Dict[str, Any]:
        """Get all sessions for user."""
        try:
            stub = await self.get_stub()
            request = auth_pb2.GetSessionsRequest(user_id=user_id)
            response = await stub.GetSessions(request)
            
            sessions = []
            for sess in response.sessions:
                sessions.append({
                    "device_id": sess.device_id,
                    "client_id": sess.client_id,
                    "ip_address": sess.ip_address or None,
                    "created_at": sess.created_at.ToDatetime() if sess.HasField("created_at") else None,
                    "last_activity": sess.last_activity.ToDatetime() if sess.HasField("last_activity") else None,
                })
            
            return {
                "sessions": sessions,
                "total_clients": response.total_clients,
                "total_sessions": response.total_sessions,
            }
        except grpc.RpcError as e:
            await self.handle_grpc_error(e)

    def _user_data_to_dict(self, user: auth_pb2.UserData) -> Dict[str, Any]:
        """Convert gRPC UserData message to dict."""
        allowed_apps = []
        for app in user.allowed_apps:
            allowed_apps.append({
                "id": app.id,
                "code": app.code,
                "name": app.name,
            })
        
        return {
            "id": user.id,
            "role": user.role,
            "name": user.name or None,
            "email": user.email or None,
            "avatar_url": user.avatar_url or None,
            "allowed_apps": allowed_apps,
        }

    def _login_response_to_dict(self, response: auth_pb2.LoginResponse) -> Dict[str, Any]:
        """Convert gRPC LoginResponse to dict."""
        return {
            "success": response.success,
            "error": response.error if response.HasField("error") else None,
            "sso_token": response.sso_token or None,
            "access_token": response.access_token or None,
            "refresh_token": response.refresh_token or None,
            "token_type": response.token_type,
            "expires_in": response.expires_in if response.HasField("expires_in") else None,
            "user": self._user_data_to_dict(response.user) if response.HasField("user") else None,
        }
