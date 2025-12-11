"""
Application Constants
Konstanta-konstanta yang digunakan di seluruh aplikasi.
Berbeda dengan Settings yang bisa dikonfigurasi via environment variables,
Constants adalah nilai tetap yang tidak berubah.
"""


class ValidationConstants:
    """Constants untuk validation error messages"""

    # Mapping tipe error Pydantic v2 ke bahasa Indonesia
    ERROR_TRANSLATIONS = {
        # Missing/Required fields
        "missing": "Field {field} wajib diisi",
        # Email validation
        "value_error": "Format {field} tidak valid",
        # Number validations
        "greater_than": "Nilai {field} harus lebih besar dari {gt}",
        "greater_than_equal": "Nilai {field} harus lebih besar atau sama dengan {ge}",
        "less_than": "Nilai {field} harus lebih kecil dari {lt}",
        "less_than_equal": "Nilai {field} harus lebih kecil atau sama dengan {le}",
        # String validations
        "string_too_short": "Panjang {field} minimal {min_length} karakter",
        "string_too_long": "Panjang {field} maksimal {max_length} karakter",
        # List validations
        "too_short": "Jumlah item {field} minimal {min_length}",
        "too_long": "Jumlah item {field} maksimal {max_length}",
        # Type errors
        "int_type": "Field {field} harus berupa angka bulat",
        "int_parsing": "Field {field} harus berupa angka bulat yang valid",
        "float_type": "Field {field} harus berupa angka desimal",
        "float_parsing": "Field {field} harus berupa angka desimal yang valid",
        "string_type": "Field {field} harus berupa teks",
        "bool_type": "Field {field} harus berupa boolean (true/false)",
        "bool_parsing": "Field {field} harus berupa boolean (true/false)",
        "list_type": "Field {field} harus berupa list/array",
        "dict_type": "Field {field} harus berupa object",
        "date_type": "Field {field} harus berupa tanggal yang valid",
        "date_parsing": "Field {field} harus berupa tanggal yang valid",
        "datetime_type": "Field {field} harus berupa datetime yang valid",
        "datetime_parsing": "Field {field} harus berupa datetime yang valid",
        "json_invalid": "Field {field} harus berupa JSON yang valid",
        "enum": "Field {field} harus berupa salah satu dari nilai yang valid",
    }


class FileUploadConstants:
    """Constants untuk file upload validations"""

    # Allowed MIME types
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
    }

    ALLOWED_DOCUMENT_TYPES = {
        "application/pdf",
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-excel",  # .xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "text/plain",
        "text/csv",
    }

    ALLOWED_VIDEO_TYPES = {
        "video/mp4",
        "video/mpeg",
        "video/quicktime",  # .mov
        "video/x-msvideo",  # .avi
        "video/webm",
    }

    # File extensions mapping untuk fallback validation
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv"}
    VIDEO_EXTENSIONS = {".mp4", ".mpeg", ".mov", ".avi", ".webm"}

    # Default file size limits (bytes) - bisa di-override dari Settings
    DEFAULT_MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
    DEFAULT_MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10 MB
    DEFAULT_MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB


class AppConstants:
    """General application constants"""

    # HTTP Status descriptions
    HTTP_200_OK = "Success"
    HTTP_201_CREATED = "Created"
    HTTP_204_NO_CONTENT = "No Content"
    HTTP_400_BAD_REQUEST = "Bad Request"
    HTTP_401_UNAUTHORIZED = "Unauthorized"
    HTTP_403_FORBIDDEN = "Forbidden"
    HTTP_404_NOT_FOUND = "Not Found"
    HTTP_422_UNPROCESSABLE_ENTITY = "Validation Error"
    HTTP_500_INTERNAL_SERVER_ERROR = "Internal Server Error"

    # Response messages
    MSG_DATA_NOT_FOUND = "Data tidak ditemukan"
    MSG_DATA_ALREADY_EXISTS = "Data sudah ada"
    MSG_OPERATION_SUCCESS = "Operasi berhasil"
    MSG_OPERATION_FAILED = "Operasi gagal"
    MSG_UNAUTHORIZED = "Anda tidak memiliki akses"
    MSG_FORBIDDEN = "Akses ditolak"
    MSG_VALIDATION_ERROR = "Data tidak valid"


class AttendanceConstants:
    VALID_STATUSES = ["present", "absent", "leave", "hybrid", "invalid"]
    VALID_TYPES = ["today", "weekly", "monthly"]
