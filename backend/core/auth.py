"""JWT and password utilities for Controle PGM authentication."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from core.config import settings
from core.exceptions import (
    PasswordPolicyError,
    TokenExpiredError,
    UnauthorizedError,
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Hashed password string.
    """
    salt = bcrypt.gensalt(rounds=settings.bcrypt_cost_factor)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password to verify.
        hashed_password: Stored bcrypt hash.

    Returns:
        True if password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def validate_password_policy(password: str) -> None:
    """
    Validate password meets policy requirements.

    Requirements:
    - Minimum 8 characters
    - At least 1 letter
    - At least 1 number

    Args:
        password: Password to validate.

    Raises:
        PasswordPolicyError: If password doesn't meet requirements.
    """
    if len(password) < settings.password_min_length:
        raise PasswordPolicyError(
            f"Senha deve ter no mínimo {settings.password_min_length} caracteres"
        )

    if not re.search(r"[a-zA-Z]", password):
        raise PasswordPolicyError("Senha deve conter pelo menos 1 letra")

    if not re.search(r"\d", password):
        raise PasswordPolicyError("Senha deve conter pelo menos 1 número")


def create_token(user_id: str, email: str, role: str, name: str) -> str:
    """
    Create a JWT token for the user.

    Args:
        user_id: User's unique identifier.
        email: User's email address.
        role: User's role (admin or user).
        name: User's display name.

    Returns:
        Encoded JWT token string.
    """
    now = datetime.now(UTC)
    expiration = now + timedelta(hours=settings.jwt_expiration_hours)

    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "name": name,
        "iat": now,
        "exp": expiration,
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify.

    Returns:
        Decoded token payload.

    Raises:
        TokenExpiredError: If token has expired.
        UnauthorizedError: If token is invalid.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Token inválido")


def extract_user_from_token(token: str) -> dict[str, Any]:
    """
    Extract user information from token.

    Args:
        token: JWT token.

    Returns:
        Dictionary with user_id, email, role, and name.
    """
    payload = verify_token(token)
    return {
        "user_id": payload["sub"],
        "email": payload["email"],
        "role": payload["role"],
        "name": payload["name"],
    }


def create_auth_cookie(token: str) -> dict[str, str]:
    """
    Create cookie headers for authentication.

    Args:
        token: JWT token to set in cookie.

    Returns:
        Dictionary with Set-Cookie header value.
    """
    max_age = settings.jwt_expiration_hours * 3600
    secure = "Secure; " if settings.is_production else ""

    cookie_value = (
        f"auth_token={token}; HttpOnly; {secure}SameSite=Strict; Path=/; Max-Age={max_age}"
    )

    return {"Set-Cookie": cookie_value}


def create_logout_cookie() -> dict[str, str]:
    """
    Create cookie headers to clear authentication.

    Returns:
        Dictionary with Set-Cookie header value to expire the cookie.
    """
    secure = "Secure; " if settings.is_production else ""

    cookie_value = f"auth_token=; HttpOnly; {secure}SameSite=Strict; Path=/; Max-Age=0"

    return {"Set-Cookie": cookie_value}


def extract_token_from_cookie(cookie_header: str | None) -> str | None:
    """
    Extract auth token from Cookie header.

    Args:
        cookie_header: Value of Cookie header.

    Returns:
        Token string or None if not found.
    """
    if not cookie_header:
        return None

    cookies = {}
    for cookie in cookie_header.split(";"):
        cookie = cookie.strip()
        if "=" in cookie:
            name, value = cookie.split("=", 1)
            cookies[name.strip()] = value.strip()

    return cookies.get("auth_token")
