"""
Validation Utilities
Utilities untuk handling validation errors
"""
from pydantic_core import ErrorDetails
from app.config.constants import ValidationConstants


def translate_validation_error(error: ErrorDetails) -> str:
    """
    Menerjemahkan error validation Pydantic ke bahasa Indonesia.
    
    Args:
        error: Dictionary error dari Pydantic ValidationError.errors()
        
    Returns:
        String error message dalam bahasa Indonesia
        
    Example:
        >>> from pydantic import ValidationError
        >>> try:
        ...     # Some validation
        ... except ValidationError as e:
        ...     for error in e.errors():
        ...         translated = translate_validation_error(error)
    """
    error_type = error.get("type", "")
    field = " -> ".join(str(loc) for loc in error.get("loc", []) if loc != "body")
    msg = error.get("msg", "")
    ctx = error.get("ctx", {})
    
    # Cek apakah ada custom message dari ValueError (prioritas tertinggi)
    # ValueError akan memiliki type "value_error" dan message kustom
    if error_type == "value_error" and msg and not msg.startswith("Value error"):
        # Langsung return message asli jika sudah custom
        return msg
    
    # Untuk Value error yang dihasilkan oleh validator, ambil dari context
    if error_type == "value_error" and "error" in ctx:
        return str(ctx["error"])
    
    # Special handling untuk enum type dengan menampilkan nilai yang valid
    if error_type == "enum":
        expected = ctx.get("expected", "")
        if expected:
            # expected format: "'value1', 'value2' or 'value3'"
            return f"Field {field} harus berupa salah satu dari: {expected}"
        return f"Field {field} harus berupa salah satu dari nilai yang valid"
    
    # Cari template dari error type
    template = ValidationConstants.ERROR_TRANSLATIONS.get(error_type)
    
    if template:
        try:
            return template.format(field=field, **ctx)
        except (KeyError, ValueError):
            # Jika format gagal, coba tanpa context
            try:
                return template.format(field=field)
            except:
                pass
    
    # Fallback ke message default dengan field name
    if field:
        return f"Field {field}: {msg}"
    return msg
