"""
Employee Validators - Reusable validation utilities
"""

from typing import Optional
import re


class EmployeeValidator:
    """Reusable validation methods for employee data"""

    VALID_TYPES = ["on_site", "hybrid", "ho"]
    VALID_GENDERS = ["male", "female"]

    @staticmethod
    def validate_employee_number(number: str) -> str:
        if not number or not number.strip():
            raise ValueError("Employee number is required")
        return number.strip().upper()

    @staticmethod
    def validate_employee_type(emp_type: Optional[str]) -> Optional[str]:
        if emp_type is None:
            return None
        if emp_type not in EmployeeValidator.VALID_TYPES:
            raise ValueError(f"Type must be one of: {', '.join(EmployeeValidator.VALID_TYPES)}")
        return emp_type

    @staticmethod
    def validate_gender(gender: Optional[str]) -> Optional[str]:
        if gender is None:
            return None
        if gender not in EmployeeValidator.VALID_GENDERS:
            raise ValueError(f"Gender must be one of: {', '.join(EmployeeValidator.VALID_GENDERS)}")
        return gender

    @staticmethod
    def validate_phone(phone: Optional[str]) -> Optional[str]:
        if phone is None:
            return None
        cleaned = phone.strip().replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError("Phone must contain only digits and +")
        return phone.strip()

    @staticmethod
    def validate_name(name: str, field: str = "Name") -> str:
        if not name or not name.strip():
            raise ValueError(f"{field} is required")
        return name.strip()

    @staticmethod
    def build_full_name(first_name: str, last_name: str) -> str:
        return f"{first_name.strip()} {last_name.strip()}"

    @staticmethod
    def split_full_name(full_name: str) -> tuple:
        parts = (full_name or "").split(" ", 1)
        first_name = parts[0] if len(parts) > 0 else ""
        last_name = parts[1] if len(parts) > 1 else ""
        return first_name, last_name
