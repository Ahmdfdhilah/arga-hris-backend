import grpc
from typing import Optional
from app.config.settings import settings
from app.core.exceptions import GRPCConnectionException, GRPCException
from app.core.utils.logging import get_logger

logger = get_logger(__name__)


class BaseGRPCClient:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.address = settings.workforce_grpc_address
        self._channel: Optional[grpc.aio.Channel] = None

    async def get_channel(self) -> grpc.aio.Channel:
        if self._channel is None:
            try:
                self._channel = grpc.aio.insecure_channel(self.address)
                await self._channel.channel_ready()
                logger.info(f"Connected to {self.service_name} at {self.address}")
            except Exception as e:
                logger.error(f"Failed to connect to {self.service_name}: {str(e)}")
                raise GRPCConnectionException(self.service_name, str(e))
        return self._channel

    async def close(self):
        if self._channel:
            await self._channel.close()
            self._channel = None
            logger.info(f"Closed connection to {self.service_name}")

    async def handle_grpc_error(self, error: grpc.RpcError):
        from app.core.exceptions import (
            BadRequestException,
            NotFoundException,
            ConflictException,
            UnprocessableEntityException,
            InternalServerException,
            ServiceUnavailableException,
        )

        status_code = error.code()
        details = error.details()

        logger.error(
            f"gRPC error from {self.service_name}: {status_code} - {details}"
        )

        # Map gRPC status code ke HTTP status code yang sesuai
        if status_code == grpc.StatusCode.NOT_FOUND:
            # 404 Not Found
            raise NotFoundException(f"{details}")

        elif status_code == grpc.StatusCode.INVALID_ARGUMENT:
            # 400 Bad Request - validation/input error
            raise BadRequestException(f"{details}")

        elif status_code == grpc.StatusCode.ALREADY_EXISTS:
            # 409 Conflict - duplicate resource
            raise ConflictException(f"{details}")

        elif status_code == grpc.StatusCode.FAILED_PRECONDITION:
            # 422 Unprocessable Entity - business logic error
            raise UnprocessableEntityException(f"{details}")

        elif status_code == grpc.StatusCode.PERMISSION_DENIED:
            # 403 Forbidden
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException(f"{details}")

        elif status_code == grpc.StatusCode.UNAUTHENTICATED:
            # 401 Unauthorized
            from app.core.exceptions import UnauthorizedException
            raise UnauthorizedException(f"{details}")

        elif status_code == grpc.StatusCode.UNAVAILABLE:
            # 503 Service Unavailable
            raise ServiceUnavailableException(f"{details}")

        elif status_code == grpc.StatusCode.INTERNAL:
            # 500 Internal Server Error
            raise InternalServerException(f"{details}")

        else:
            # Default: 502 Bad Gateway untuk error yang tidak terduga
            raise GRPCException(self.service_name, f"{status_code}: {details}")
