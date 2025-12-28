# gRPC module for HRIS Backend
# Includes both server (for Employee/OrgUnit master data) and clients (for SSO)
#
# NOTE: Server components (grpc_server, handlers) are NOT imported here to avoid
# circular imports. Import them directly from app.grpc.server when needed.

# Client components only - safe to import from services
from app.grpc.base_client import BaseGRPCClient
from app.grpc.clients.sso_client import SSOUserGRPCClient, SSOAuthGRPCClient

__all__ = [
    # Client
    "BaseGRPCClient",
    "SSOUserGRPCClient",
    "SSOAuthGRPCClient",
]
