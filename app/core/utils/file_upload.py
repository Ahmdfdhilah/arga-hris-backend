"""
File Upload utility

Provides functions untuk handle multipart file uploads dengan validasi.
Support berbagai tipe file (images, documents, videos, dll).
"""

from fastapi import UploadFile
from typing import List, Optional, Tuple
import os
import imghdr

from app.config.settings import settings
from app.config.constants import FileUploadConstants
from app.core.exceptions import FileValidationError


async def validate_file_type(
    file: UploadFile, allowed_types: set, check_magic: bool = True
) -> str:
    """
    Validate file type berdasarkan MIME type

    Args:
        file: UploadFile object dari FastAPI
        allowed_types: Set dari allowed MIME types
        check_magic: Apakah mau check MIME type pake magic bytes (lebih aman)

    Returns:
        str: Validated MIME type

    Raises:
        FileValidationError: Jika file type tidak diizinkan

    Example:
        >>> file_type = await validate_file_type(
        ...     file=uploaded_file,
        ...     allowed_types=FileUploadConstants.ALLOWED_IMAGE_TYPES
        ... )
    """
    # Check content type dari upload
    content_type = file.content_type

    # Handle None content_type
    if content_type is None:
        raise FileValidationError("File content type is missing")

    if content_type not in allowed_types:
        raise FileValidationError(
            f"File type '{content_type}' tidak diizinkan. "
            f"Allowed types: {', '.join(allowed_types)}"
        )

    # Additional check menggunakan imghdr untuk image files (optional tapi recommended)
    if check_magic and content_type.startswith('image/'):
        # Read first 512 bytes untuk detect image type
        content = await file.read(512)
        await file.seek(0)  # Reset file pointer

        # Detect image type dari content
        image_type = imghdr.what(None, h=content)
        
        if image_type:
            # Map imghdr result to MIME type
            mime_map = {
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'bmp': 'image/bmp'
            }
            detected_mime = mime_map.get(image_type)
            
            if detected_mime and detected_mime not in allowed_types:
                raise FileValidationError(
                    f"File content tidak sesuai dengan extension. Detected type: {detected_mime}"
                )

    return content_type


async def validate_file_size(file: UploadFile, max_size: int) -> int:
    """
    Validate ukuran file

    Args:
        file: UploadFile object dari FastAPI
        max_size: Maximum size dalam bytes

    Returns:
        int: Ukuran file dalam bytes

    Raises:
        FileValidationError: Jika file terlalu besar

    Example:
        >>> size = await validate_file_size(
        ...     file=uploaded_file,
        ...     max_size=settings.MAX_IMAGE_SIZE
        ... )
    """
    # Get file size
    content = await file.read()
    file_size = len(content)
    await file.seek(0)  # Reset file pointer

    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise FileValidationError(
            f"File terlalu besar. Maximum size: {max_size_mb:.2f} MB"
        )

    return file_size


async def validate_image_file(
    file: UploadFile, max_size: Optional[int] = None
) -> Tuple[str, int]:
    """
    Validate image file (type + size)

    Args:
        file: UploadFile object
        max_size: Maximum file size (default 5 MB)

    Returns:
        Tuple[str, int]: (MIME type, file size)

    Raises:
        FileValidationError: Jika validasi gagal

    Example:
        >>> mime_type, size = await validate_image_file(uploaded_file)
    """
    if max_size is None:
        max_size = settings.MAX_IMAGE_SIZE
    mime_type = await validate_file_type(file, FileUploadConstants.ALLOWED_IMAGE_TYPES)
    file_size = await validate_file_size(file, max_size)
    return mime_type, file_size


async def validate_document_file(
    file: UploadFile, max_size: Optional[int] = None
) -> Tuple[str, int]:
    """
    Validate document file (type + size)

    Args:
        file: UploadFile object
        max_size: Maximum file size (default 10 MB)

    Returns:
        Tuple[str, int]: (MIME type, file size)

    Raises:
        FileValidationError: Jika validasi gagal

    Example:
        >>> mime_type, size = await validate_document_file(uploaded_file)
    """
    if max_size is None:
        max_size = settings.MAX_DOCUMENT_SIZE
    mime_type = await validate_file_type(file, FileUploadConstants.ALLOWED_DOCUMENT_TYPES)
    file_size = await validate_file_size(file, max_size)
    return mime_type, file_size


async def validate_video_file(
    file: UploadFile, max_size: Optional[int] = None
) -> Tuple[str, int]:
    """
    Validate video file (type + size)

    Args:
        file: UploadFile object
        max_size: Maximum file size (default 50 MB)

    Returns:
        Tuple[str, int]: (MIME type, file size)

    Raises:
        FileValidationError: Jika validasi gagal

    Example:
        >>> mime_type, size = await validate_video_file(uploaded_file)
    """
    if max_size is None:
        max_size = settings.MAX_VIDEO_SIZE
    mime_type = await validate_file_type(file, FileUploadConstants.ALLOWED_VIDEO_TYPES)
    file_size = await validate_file_size(file, max_size)
    return mime_type, file_size


async def validate_multiple_files(
    files: List[UploadFile], max_files: int, allowed_types: set, max_size: int
) -> List[Tuple[str, int]]:
    """
    Validate multiple files sekaligus

    Args:
        files: List of UploadFile objects
        max_files: Maximum jumlah files yang diizinkan
        allowed_types: Set dari allowed MIME types
        max_size: Maximum size per file

    Returns:
        List[Tuple[str, int]]: List of (MIME type, file size) untuk tiap file

    Raises:
        FileValidationError: Jika validasi gagal

    Example:
        >>> results = await validate_multiple_files(
        ...     files=uploaded_files,
        ...     max_files=5,
        ...     allowed_types=FileUploadConstants.ALLOWED_IMAGE_TYPES,
        ...     max_size=settings.MAX_IMAGE_SIZE
        ... )
    """
    # Check jumlah files
    if len(files) > max_files:
        raise FileValidationError(f"Terlalu banyak files. Maximum: {max_files} files")

    # Validate tiap file
    results = []
    for file in files:
        mime_type = await validate_file_type(file, allowed_types)
        file_size = await validate_file_size(file, max_size)
        results.append((mime_type, file_size))

    return results


def get_file_extension(filename: str) -> str:
    """
    Get file extension dari filename

    Args:
        filename: Nama file

    Returns:
        str: File extension (dengan dot, lowercase)

    Example:
        >>> ext = get_file_extension("photo.JPG")
        >>> # Result: ".jpg"
    """
    _, ext = os.path.splitext(filename)
    return ext.lower()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename untuk menghindari security issues

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename

    Example:
        >>> safe_name = sanitize_filename("../../../etc/passwd")
        >>> # Result: "etc_passwd"
    """
    # Remove path separators
    filename = filename.replace("/", "_").replace("\\", "_")

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Remove leading/trailing dots and spaces
    filename = filename.strip(". ")

    return filename


async def read_file_content(file: UploadFile) -> bytes:
    """
    Read file content dan reset file pointer

    Args:
        file: UploadFile object

    Returns:
        bytes: File content

    Example:
        >>> content = await read_file_content(uploaded_file)
    """
    content = await file.read()
    await file.seek(0)  # Reset untuk bisa dibaca lagi
    return content


async def upload_file_to_gcp(
    file: UploadFile,
    entity_type: str,
    entity_id: int,
    subfolder: str = "profile",
    allowed_types: Optional[set] = None,
    max_size: Optional[int] = None,
    return_path_only: bool = True,
) -> str:
    """
    Upload file ke GCP bucket dengan validasi (generic function untuk semua entity)

    Args:
        file: UploadFile dari FastAPI
        entity_type: Tipe entity (e.g., "account_executives", "farmers")
        entity_id: ID entity
        subfolder: Subfolder di dalam entity folder (default: "profile")
        allowed_types: Set MIME types yang diizinkan (default: FileUploadConstants.ALLOWED_IMAGE_TYPES)
        max_size: Max file size dalam bytes (default: settings.MAX_IMAGE_SIZE)
        return_path_only: If True, return path saja (recommended for DB storage). Default True.

    Returns:
        str: File path (if return_path_only=True) or signed URL (if return_path_only=False)

    Raises:
        FileValidationError: Jika validasi file gagal

    Example:
        >>> # Upload profile image untuk farmer (return path for DB)
        >>> path = await upload_file_to_gcp(
        ...     file=profile_img,
        ...     entity_type="farmers",
        ...     entity_id=123,
        ...     subfolder="profile",
        ...     return_path_only=True
        ... )

        >>> # Upload document untuk farmer (return URL for immediate use)
        >>> url = await upload_file_to_gcp(
        ...     file=doc_file,
        ...     entity_type="farmers",
        ...     entity_id=123,
        ...     subfolder="documents",
        ...     allowed_types=FileUploadConstants.ALLOWED_DOCUMENT_TYPES,
        ...     max_size=settings.MAX_DOCUMENT_SIZE,
        ...     return_path_only=False
        ... )
    """
    from app.core.utils.gcp_storage import get_gcp_storage_client

    # Default values
    if allowed_types is None:
        allowed_types = FileUploadConstants.ALLOWED_IMAGE_TYPES
    if max_size is None:
        max_size = settings.MAX_IMAGE_SIZE

    # 1. Validate file type & size
    mime_type = await validate_file_type(file, allowed_types)
    await validate_file_size(file, max_size)

    # 2. Read file content
    file_content = await read_file_content(file)

    # 3. Get storage client
    storage_client = get_gcp_storage_client()

    # 4. Generate unique filename with entity path
    filename = file.filename or "unnamed_file"
    destination_path = storage_client.generate_unique_filename(
        original_filename=filename, prefix=f"{entity_type}/{entity_id}/{subfolder}"
    )

    # 5. Upload to GCP
    file_result = storage_client.upload_file(
        file_content=file_content,
        destination_path=destination_path,
        content_type=mime_type,
        return_path_only=return_path_only,
    )

    return file_result


def generate_signed_url_from_path(file_path: Optional[str], expiration_days: int = 7) -> Optional[str]:
    """
    Generate signed URL from GCP storage file path (generic function)

    Args:
        file_path: GCP storage path (e.g., "attendances/123/check_in/2025-01-01/file.jpg")
        expiration_days: URL expiration in days (default: 7 days)

    Returns:
        Optional[str]: Signed URL or None if path is None/empty

    Example:
        >>> # Generate signed URL from path
        >>> url = generate_signed_url_from_path(
        ...     "attendances/123/check_in/2025-01-01/selfie.jpg",
        ...     expiration_days=7
        ... )
    """
    from app.core.utils.gcp_storage import get_gcp_storage_client
    from datetime import timedelta
    import logging

    logger = logging.getLogger(__name__)

    if not file_path:
        logger.warning("generate_signed_url_from_path: file_path is None or empty")
        return None

    try:
        logger.info(f"Generating signed URL for path: {file_path}")
        storage_client = get_gcp_storage_client()
        blob = storage_client.bucket.blob(file_path)
        
        # Generate signed URL directly without checking file existence
        # (assume file exists if path is stored in DB)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=expiration_days),
            method="GET"
        )
        logger.info(f"Successfully generated signed URL for: {file_path}")
        return url
    except Exception as e:
        logger.error(f"Error generating signed URL from path '{file_path}': {e}", exc_info=True)
        return None


def delete_file_from_gcp_url(file_url: str) -> bool:
    """
    Delete file dari GCP bucket berdasarkan URL (generic function)

    Args:
        file_url: URL file yang akan dihapus (public URL atau signed URL)

    Returns:
        bool: True jika berhasil dihapus, False jika gagal

    Example:
        >>> # Delete file by URL
        >>> success = delete_file_from_gcp_url(
        ...     "https://storage.googleapis.com/bucket-name/farmers/123/profile/file.jpg"
        ... )
    """
    from app.core.utils.gcp_storage import get_gcp_storage_client

    try:
        if not file_url:
            return False

        storage_client = get_gcp_storage_client()

        # Extract file path from URL
        # URL format: https://storage.googleapis.com/bucket-name/path/to/file.jpg
        if storage_client.bucket_name in file_url:
            file_path = file_url.split(f"{storage_client.bucket_name}/")[-1]

            # Remove query parameters jika ada (untuk signed URLs)
            file_path = file_path.split("?")[0]

            return storage_client.delete_file(file_path)

        return False
    except Exception as e:
        print(f"Error deleting file from GCP: {e}")
        return False
