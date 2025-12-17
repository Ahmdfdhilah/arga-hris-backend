from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from app.config.constants import FileUploadConstants


class Settings(BaseSettings):
    APP_NAME: str = Field(...)
    APP_VERSION: str = Field(...)
    DEBUG: bool = Field(...)
    API_PREFIX: str = Field(...)

    POSTGRES_SERVER: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_DB: str = Field(...)
    POSTGRES_PORT: str = Field(...)

    REDIS_HOST: str = Field(...)
    REDIS_PORT: int = Field(...)
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # RabbitMQ
    RABBITMQ_HOST: str = Field(default="localhost")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_USER: str = Field(default="guest")
    RABBITMQ_PASSWORD: str = Field(default="guest")
    RABBITMQ_VHOST: str = Field(default="/")

    GCP_CREDENTIALS_PATH: str = Field(
        default="app/credentials/gcp/your-gcp-credentials.json"
    )
    GCP_BUCKET_NAME: str = Field(default="sahabat-arga-bucket")

    JWT_PUBLIC_KEY_PATH: str = Field(default="./jwt_public.pem")
    JWT_ALGORITHM: str = Field(default="RS256")

    WORKFORCE_GRPC_HOST: str = Field(...)
    WORKFORCE_GRPC_PORT: int = Field(...)

    # SSO Service for user sync
    SSO_SERVICE_URL: str = Field(default="http://localhost:8001")
    SSO_SERVICE_API_KEY: str = Field(default="your-secret-api-key-here")
    SSO_HRIS_APPLICATION_ID: int = Field(
        default=1, description="Application ID for HRIS in SSO"
    )
    SSO_GRPC_HOST: str = Field(default="localhost")
    SSO_GRPC_PORT: int = Field(default=50051)

    # gRPC Server Settings (HRIS as master for Employee/OrgUnit)
    GRPC_HOST: str = Field(default="0.0.0.0")
    GRPC_PORT: int = Field(default=50053)
    
    # gRPC Client Settings
    GRPC_MAX_MESSAGE_SIZE: int = Field(default=15 * 1024 * 1024)
    GRPC_TIMEOUT_SECONDS: int = Field(default=30)

    # Nominatim OpenStreetMap Geocoding Service
    NOMINATIM_BASE_URL: str = Field(
        default="https://nominatim.openstreetmap.org",
        description="Base URL for Nominatim API",
    )
    NOMINATIM_USER_AGENT: str = Field(
        default="ARGA-HRIS/1.0", description="User agent for Nominatim API (required)"
    )
    NOMINATIM_TIMEOUT: float = Field(
        default=10.0, description="Timeout for Nominatim API requests in seconds"
    )

    SUPER_ADMIN_EMAIL: str | None = None
    SUPER_ADMIN_SSO_ID: str | None = None
    SUPER_ADMIN_FIRST_NAME: str | None = None
    SUPER_ADMIN_LAST_NAME: str | None = None

    CORS_ORIGINS: str = Field(...)

    # File Upload Settings - size limits (bytes) dapat di-override via env
    # MIME types constants ada di app.config.constants.FileUploadConstants
    MAX_IMAGE_SIZE: int = Field(default=FileUploadConstants.DEFAULT_MAX_IMAGE_SIZE)
    MAX_DOCUMENT_SIZE: int = Field(
        default=FileUploadConstants.DEFAULT_MAX_DOCUMENT_SIZE
    )
    MAX_VIDEO_SIZE: int = Field(default=FileUploadConstants.DEFAULT_MAX_VIDEO_SIZE)

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def sync_database_url(self) -> str:
        """Database URL for synchronous operations (scripts, migrations)"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def workforce_grpc_address(self) -> str:
        return f"{self.WORKFORCE_GRPC_HOST}:{self.WORKFORCE_GRPC_PORT}"

    @property
    def sso_grpc_address(self) -> str:
        return f"{self.SSO_GRPC_HOST}:{self.SSO_GRPC_PORT}"

    # File Upload Constants - exposed as properties for file_upload.py compatibility
    @property
    def ALLOWED_IMAGE_TYPES(self) -> set:
        return FileUploadConstants.ALLOWED_IMAGE_TYPES

    @property
    def ALLOWED_DOCUMENT_TYPES(self) -> set:
        return FileUploadConstants.ALLOWED_DOCUMENT_TYPES

    @property
    def ALLOWED_VIDEO_TYPES(self) -> set:
        return FileUploadConstants.ALLOWED_VIDEO_TYPES

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


def get_settings() -> Settings:
    """
    Factory function to create Settings instance from environment variables.

    Using model_validate() with empty dict explicitly tells Pydantic to validate
    and populate all fields from environment variables (via .env file configured
    in model_config). This is type-safe and doesn't trigger Pylance warnings.
    """
    return Settings.model_validate({})


settings = get_settings()
