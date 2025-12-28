"""
Google Cloud Storage utility

Provides functions to upload, delete, and get URLs for files in GCP bucket.
Menggunakan service account credentials untuk autentikasi.
Project ID diambil dari credentials JSON, bucket name dari settings.
"""

import os
from typing import Optional
from google.cloud import storage
from google.oauth2 import service_account
import uuid
from datetime import timedelta


class GCPStorageClient:
    """Client untuk berinteraksi dengan Google Cloud Storage"""

    def __init__(self, credentials_path: str, bucket_name: str):
        """
        Initialize GCP Storage Client

        Args:
            credentials_path: Path ke service account credentials JSON file
            bucket_name: Nama bucket GCP (dari settings)
        """
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )

        project_id = credentials.project_id

        # Initialize storage client
        self.client = storage.Client(
            credentials=credentials,
            project=project_id
        )

        self.bucket = self.client.bucket(bucket_name)
        self.bucket_name = bucket_name
        self.project_id = project_id

    def upload_file(
        self,
        file_content: bytes,
        destination_path: str,
        content_type: Optional[str] = None,
        return_path_only: bool = False,
    ) -> str:
        """
        Upload file ke GCP bucket

        Args:
            file_content: Content file dalam bytes
            destination_path: Path tujuan di bucket (e.g., "farmers/photos/file.jpg")
            content_type: MIME type dari file (e.g., "image/jpeg")
            return_path_only: If True, return path saja (not signed URL). Default False for backward compatibility.

        Returns:
            str: File path (if return_path_only=True) or signed URL (if return_path_only=False)

        Example:
            >>> from app.core.config import settings
            >>> client = GCPStorageClient(
            ...     settings.GCP_CREDENTIALS_PATH,
            ...     settings.GCP_BUCKET_NAME
            ... )
            >>> # Return path only (recommended for database storage)
            >>> path = client.upload_file(
            ...     file_content=file_bytes,
            ...     destination_path="farmers/photos/farmer123.jpg",
            ...     content_type="image/jpeg",
            ...     return_path_only=True
            ... )
            >>> # Or return signed URL (for immediate use)
            >>> url = client.upload_file(
            ...     file_content=file_bytes,
            ...     destination_path="farmers/photos/farmer123.jpg",
            ...     content_type="image/jpeg"
            ... )
        """
        blob = self.bucket.blob(destination_path)

        # Upload file
        if content_type is not None:
            blob.upload_from_string(
                file_content,
                content_type=content_type
            )
        else:
            blob.upload_from_string(file_content)

        # Return path only untuk disimpan di DB
        if return_path_only:
            return destination_path

        # Return signed URL (expired in 7 days) jika private
        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file dari GCP bucket

        Args:
            file_path: Path file di bucket

        Returns:
            bool: True jika berhasil, False jika gagal

        Example:
            >>> from app.core.config import settings
            >>> client = GCPStorageClient(
            ...     settings.GCP_CREDENTIALS_PATH,
            ...     settings.GCP_BUCKET_NAME
            ... )
            >>> success = client.delete_file("farmers/photos/farmer123.jpg")
        """
        try:
            blob = self.bucket.blob(file_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_url(
        self,
        file_path: str,
        expiration: timedelta = timedelta(days=7),
        bucket_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Get signed URL untuk file (untuk private files)

        Args:
            file_path: Path file di bucket
            expiration: Waktu expired URL (default 7 hari)
            bucket_name: Nama bucket (optional). Jika tidak diisi, pakai bucket default.
                        Berguna untuk generate signed URL dari bucket lain (e.g., SSO bucket).

        Returns:
            Optional[str]: Signed URL atau None jika file tidak ada

        Example:
            >>> from app.core.config import settings
            >>> client = GCPStorageClient(
            ...     settings.GCP_CREDENTIALS_PATH,
            ...     settings.GCP_BUCKET_NAME
            ... )
            >>> # Default bucket (HRIS)
            >>> url = client.get_file_url("farmers/photos/farmer123.jpg")
            >>>
            >>> # Bucket lain (SSO)
            >>> url = client.get_file_url(
            ...     "users/avatars/user123.jpg",
            ...     bucket_name=settings.GCP_SSO_BUCKET_NAME
            ... )
        """
        try:
            # Pilih bucket: custom bucket atau default bucket
            target_bucket = self.client.bucket(bucket_name) if bucket_name else self.bucket
            blob = target_bucket.blob(file_path)

            # Check if file exists
            if not blob.exists():
                return None

            # Always return signed URL for security and type safety
            # Public URLs can be accessed via signed URLs as well
            return blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
        except Exception as e:
            print(f"Error getting file URL: {e}")
            return None

    def get_sso_file_url(
        self,
        file_path: str,
        expiration: timedelta = timedelta(days=7)
    ) -> Optional[str]:
        """
        Shortcut untuk generate signed URL dari SSO bucket.

        Fungsi ini khusus untuk file-file yang berasal dari service SSO
        (misal: user avatar_path yang disimpan di users table).

        Args:
            file_path: Path file di SSO bucket
            expiration: Waktu expired URL (default 7 hari)

        Returns:
            Optional[str]: Signed URL atau None jika file tidak ada

        Example:
            >>> from app.core.config import settings
            >>> client = GCPStorageClient(
            ...     settings.GCP_CREDENTIALS_PATH,
            ...     settings.GCP_BUCKET_NAME
            ... )
            >>> # Generate URL untuk avatar yang ada di bucket SSO
            >>> url = client.get_sso_file_url("users/avatars/user123.jpg")
        """
        from app.config.settings import settings
        return self.get_file_url(
            file_path=file_path,
            expiration=expiration,
            bucket_name=settings.GCP_SSO_BUCKET_NAME
        )

    def file_exists(self, file_path: str) -> bool:
        """
        Check apakah file ada di bucket

        Args:
            file_path: Path file di bucket

        Returns:
            bool: True jika file ada, False jika tidak

        Example:
            >>> from app.core.config import settings
            >>> client = GCPStorageClient(
            ...     settings.GCP_CREDENTIALS_PATH,
            ...     settings.GCP_BUCKET_NAME
            ... )
            >>> exists = client.file_exists("farmers/photos/farmer123.jpg")
        """
        blob = self.bucket.blob(file_path)
        return blob.exists()

    def generate_unique_filename(
        self,
        original_filename: str,
        prefix: str = ""
    ) -> str:
        """
        Generate unique filename dengan UUID

        Args:
            original_filename: Nama file asli
            prefix: Prefix untuk filename (e.g., "farmers/photos")

        Returns:
            str: Unique filename dengan format: prefix/uuid_filename.ext

        Example:
            >>> from app.core.config import settings
            >>> client = GCPStorageClient(
            ...     settings.GCP_CREDENTIALS_PATH,
            ...     settings.GCP_BUCKET_NAME
            ... )
            >>> filename = client.generate_unique_filename(
            ...     "photo.jpg",
            ...     prefix="farmers/photos"
            ... )
            >>> # Result: "farmers/photos/123e4567-e89b-12d3-a456-426614174000_photo.jpg"
        """
        # Extract file extension
        _, ext = os.path.splitext(original_filename)

        # Generate unique ID
        unique_id = str(uuid.uuid4())

        # Combine
        unique_filename = f"{unique_id}{ext}"

        if prefix:
            return f"{prefix}/{unique_filename}"

        return unique_filename


# Singleton instance
_gcp_storage_client: Optional[GCPStorageClient] = None


def get_gcp_storage_client() -> GCPStorageClient:
    """
    Get atau create GCP Storage Client (Singleton pattern)
    
    Menggunakan credentials path dan bucket name dari settings.
    Project ID otomatis dibaca dari credentials JSON.

    Returns:
        GCPStorageClient: Instance dari GCP Storage Client

    Example:
        >>> # Di service atau router
        >>> from app.utils.gcp_storage import get_gcp_storage_client
        >>> 
        >>> storage_client = get_gcp_storage_client()
        >>> url = storage_client.upload_file(
        ...     file_content=file_bytes,
        ...     destination_path="farmers/photos/photo.jpg",
        ...     content_type="image/jpeg"
        ... )
    """
    global _gcp_storage_client

    if _gcp_storage_client is None:
        from app.config.settings import settings
        
        _gcp_storage_client = GCPStorageClient(
            credentials_path=settings.GCP_CREDENTIALS_PATH,
            bucket_name=settings.GCP_BUCKET_NAME
        )

    return _gcp_storage_client