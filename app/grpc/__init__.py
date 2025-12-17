# gRPC module for HRIS Backend
# Includes both server (for Employee/OrgUnit master data) and clients (for SSO)

# Server components
from app.grpc.server import grpc_server, GRPCServer
from app.grpc.handlers import EmployeeHandler, OrgUnitHandler

# Client components
from app.grpc.base_client import BaseGRPCClient
from app.grpc.clients.sso_client import SSOUserGRPCClient, SSOAuthGRPCClient

__all__ = [
    # Server
    "grpc_server",
    "GRPCServer",
    "EmployeeHandler",
    "OrgUnitHandler",
    # Client
    "BaseGRPCClient",
    "SSOUserGRPCClient",
    "SSOAuthGRPCClient",
]
