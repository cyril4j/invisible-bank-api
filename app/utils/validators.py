"""
Validation utilities for data validation.
"""
import re
from datetime import date
from typing import Optional


def validate_ssn(ssn: str) -> bool:
    """
    Validate Social Security Number format (XXX-XX-XXXX).

    Args:
        ssn: SSN string to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    pattern = r'^\d{3}-\d{2}-\d{4}$'
    return bool(re.match(pattern, ssn))


def validate_email(email: str) -> bool:
    """
    Basic email validation.

    Args:
        email: Email string to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_age(date_of_birth: date, minimum_age: int = 18) -> bool:
    """
    Validate that person is at least minimum_age years old.

    Args:
        date_of_birth: Date of birth
        minimum_age: Minimum required age (default: 18)

    Returns:
        bool: True if person meets minimum age, False otherwise
    """
    today = date.today()
    age = today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )
    return age >= minimum_age
