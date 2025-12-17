"""
gRPC Server for HRIS Backend

Runs gRPC server alongside FastAPI for inter-service communication.
Serves Employee and OrgUnit master data.
"""

import logging
from typing import Optional

import grpc
from grpc.aio import Server

from app.config.settings import settings
from proto.employee import employee_pb2_grpc
from proto.org_unit import org_unit_pb2_grpc
from app.grpc.handlers.employee_handler import EmployeeHandler
from app.grpc.handlers.org_unit_handler import OrgUnitHandler

logger = logging.getLogger(__name__)


class GRPCServer:
    """Async gRPC server manager for HRIS master data."""
    
    def __init__(self, port: int = 50053):
        self.port = port
        self._server: Optional[Server] = None
    
    async def start(self) -> None:
        """Start the gRPC server."""
        max_msg_size = getattr(settings, 'GRPC_MAX_MESSAGE_SIZE', 15 * 1024 * 1024)
        options = [
            ('grpc.max_send_message_length', max_msg_size),
            ('grpc.max_receive_message_length', max_msg_size),
        ]
        self._server = grpc.aio.server(options=options)
        
        # Register handlers
        employee_pb2_grpc.add_EmployeeServiceServicer_to_server(EmployeeHandler(), self._server)
        org_unit_pb2_grpc.add_OrgUnitServiceServicer_to_server(OrgUnitHandler(), self._server)
        
        # Bind to port
        listen_addr = f"[::]:{self.port}"
        self._server.add_insecure_port(listen_addr)
        
        await self._server.start()
        logger.info(f"HRIS gRPC server started on port {self.port}")
    
    async def stop(self) -> None:
        """Stop the gRPC server gracefully."""
        if self._server:
            await self._server.stop(grace=5)
            logger.info("HRIS gRPC server stopped")
    
    async def wait_for_termination(self) -> None:
        """Wait for server to terminate."""
        if self._server:
            await self._server.wait_for_termination()


# Global server instance
grpc_server = GRPCServer(port=getattr(settings, 'GRPC_PORT', 50053))
