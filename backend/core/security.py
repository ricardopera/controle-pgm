"""Security utilities for Controle PGM."""

from __future__ import annotations

import re
import secrets
import time
from uuid import UUID

import bleach


def sanitize_html(value: str) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Removes all tags and attributes, leaving only safe text.

    Args:
        value: The string to sanitize.

    Returns:
        Sanitized string.
    """
    if not value:
        return value

    return bleach.clean(value, tags=[], attributes={}, strip=True)


def sanitize_odata_string(value: str) -> str:
    """
    Sanitize a string value for use in OData filter queries.

    Escapes single quotes by doubling them (OData standard).
    Also removes potentially dangerous characters.

    Args:
        value: The string value to sanitize.

    Returns:
        Sanitized string safe for OData queries.
    """
    if not value:
        return value

    # Remove null bytes and control characters
    value = re.sub(r"[\x00-\x1f\x7f]", "", value)

    # Escape single quotes by doubling them (OData standard)
    value = value.replace("'", "''")

    # Remove potential OData injection patterns
    # These patterns could be used to break out of string context
    dangerous_patterns = [
        r"\s+or\s+",
        r"\s+and\s+",
        r"\s+eq\s+",
        r"\s+ne\s+",
        r"\s+gt\s+",
        r"\s+lt\s+",
        r"\s+ge\s+",
        r"\s+le\s+",
    ]

    for pattern in dangerous_patterns:
        value = re.sub(pattern, " ", value, flags=re.IGNORECASE)

    return value


def is_valid_uuid(value: str) -> bool:
    """
    Validate if a string is a valid UUID.

    Args:
        value: String to validate.

    Returns:
        True if valid UUID, False otherwise.
    """
    if not value:
        return False

    try:
        UUID(value, version=4)
        return True
    except (ValueError, AttributeError):
        return False


def constant_time_compare(val1: str, val2: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.

    Args:
        val1: First string.
        val2: Second string.

    Returns:
        True if strings are equal, False otherwise.
    """
    return secrets.compare_digest(val1.encode("utf-8"), val2.encode("utf-8"))


def add_random_delay(min_ms: int = 50, max_ms: int = 150) -> None:
    """
    Add a random delay to prevent timing attacks.

    This helps mask the timing difference between operations
    like "user not found" vs "password incorrect".

    Args:
        min_ms: Minimum delay in milliseconds.
        max_ms: Maximum delay in milliseconds.
    """
    delay = secrets.randbelow(max_ms - min_ms) + min_ms
    time.sleep(delay / 1000)
