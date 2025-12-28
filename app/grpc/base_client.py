"""
Base gRPC Client

Generic base class for gRPC clients with error handling and Indonesian messages.
"""

import grpc
from typing import Optional

from app.config.settings import settings
from app.core.exceptions import (
    GRPCConnectionException,
    GRPCException,
    NotFoundException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
    UnprocessableEntityException,
    InternalServerException,
    ServiceUnavailableException,
)
from app.core.utils.logging import get_logger

logger = get_logger(__name__)


class BaseGRPCClient:
    """
    Base class for async gRPC clients.
    
    Provides connection management and error handling with Indonesian messages.
    """
    
    def __init__(self, service_name: str, address: Optional[str] = None):
        self.service_name = service_name
        self.address = address or settings.sso_grpc_address
        self._channel: Optional[grpc.aio.Channel] = None
    
    async def get_channel(self) -> grpc.aio.Channel:
        """Get or create gRPC channel with message size configuration."""
        if self._channel is None:
            try:
                max_msg_size = getattr(settings, 'GRPC_MAX_MESSAGE_SIZE', 15 * 1024 * 1024)
                options = [
                    ('grpc.max_send_message_length', max_msg_size),
                    ('grpc.max_receive_message_length', max_msg_size),
                ]
                self._channel = grpc.aio.insecure_channel(self.address, options=options)
                await self._channel.channel_ready()
                logger.info(f"Connected to {self.service_name} at {self.address}")
            except Exception as e:
                logger.error(f"Failed to connect to {self.service_name}: {e}")
                raise GRPCConnectionException(self.service_name, str(e))
        return self._channel
    
    async def close(self):
        """Close the gRPC channel."""
        if self._channel:
            await self._channel.close()
            self._channel = None
            logger.info(f"Closed connection to {self.service_name}")
    
    async def handle_grpc_error(self, error: grpc.RpcError):
        """Map gRPC errors to HTTP-like exceptions with Indonesian messages."""
        status_code = error.code()
        details = error.details() or ""
        
        logger.error(f"gRPC error from {self.service_name}: {status_code} - {details}")
        
        user_message = self._parse_error_message(details)
        
        if status_code == grpc.StatusCode.NOT_FOUND:
            raise NotFoundException(user_message or "Data tidak ditemukan")
        elif status_code == grpc.StatusCode.INVALID_ARGUMENT:
            raise BadRequestException(user_message or "Data yang dikirim tidak valid")
        elif status_code == grpc.StatusCode.ALREADY_EXISTS:
            raise ConflictException(user_message or "Data sudah ada")
        elif status_code == grpc.StatusCode.FAILED_PRECONDITION:
            raise UnprocessableEntityException(user_message or "Operasi tidak dapat dilakukan")
        elif status_code == grpc.StatusCode.PERMISSION_DENIED:
            raise ForbiddenException(user_message or "Anda tidak memiliki izin untuk melakukan aksi ini")
        elif status_code == grpc.StatusCode.UNAUTHENTICATED:
            raise UnauthorizedException(user_message or "Sesi anda telah berakhir. Silakan login kembali.")
        elif status_code == grpc.StatusCode.UNAVAILABLE:
            raise ServiceUnavailableException(user_message or "Layanan sedang tidak tersedia. Silakan coba lagi nanti.")
        elif status_code == grpc.StatusCode.RESOURCE_EXHAUSTED:
            raise BadRequestException("File terlalu besar. Maksimal 15MB per file.")
        elif status_code == grpc.StatusCode.INTERNAL:
            raise InternalServerException(user_message or "Terjadi kesalahan pada server.")
        else:
            details_lower = details.lower()
            if "unique" in details_lower or "duplicate" in details_lower:
                raise ConflictException(user_message or "Data sudah ada. Tidak dapat membuat duplikat.")
            elif "foreign key" in details_lower or "fkey" in details_lower:
                raise BadRequestException(user_message or "Data referensi tidak ditemukan.")
            else:
                raise GRPCException(self.service_name, f"{status_code}: {details}")
    
    def _parse_error_message(self, details: str) -> str:
        """Parse gRPC error details to create user-friendly Indonesian message."""
        if not details:
            return ""
        
        details_lower = details.lower()
        
        # Foreign key violations
        if "foreign key" in details_lower or "fkey" in details_lower:
            if "user_id" in details_lower:
                return "User tidak ditemukan. Pastikan ID user valid."
            if "employee_id" in details_lower:
                return "Karyawan tidak ditemukan."
            if "org_unit_id" in details_lower:
                return "Unit organisasi tidak ditemukan."
            return "Data referensi tidak ditemukan. Pastikan data terkait sudah ada."
        
        # Unique constraint violations
        if "unique" in details_lower or "duplicate" in details_lower:
            if "phone" in details_lower:
                return "Nomor telepon sudah terdaftar."
            if "email" in details_lower:
                return "Email sudah terdaftar."
            if "nip" in details_lower or "employee_id" in details_lower:
                return "NIP sudah terdaftar."
            return "Data sudah ada. Tidak dapat membuat duplikat."
        
        # Not null violations
        if "not null" in details_lower or "notnull" in details_lower:
            return "Data wajib tidak boleh kosong."
        
        # Validation errors
        if "validation" in details_lower or "invalid" in details_lower:
            return "Data yang dikirim tidak valid."
        
        # Default - don't expose internal error details
        return ""
