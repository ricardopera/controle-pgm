"""Unit tests for authentication utilities."""

import pytest

from core.auth import (
    create_auth_cookie,
    create_logout_cookie,
    create_token,
    extract_token_from_cookie,
    extract_user_from_token,
    hash_password,
    validate_password_policy,
    verify_password,
    verify_token,
)
from core.exceptions import (
    PasswordPolicyError,
    UnauthorizedError,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_hash_password_returns_different_hash(self):
        """Test that hashing the same password returns different hashes."""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Different hashes due to salt
        assert hash1 != hash2

    def test_verify_password_success(self):
        """Test password verification with correct password."""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_failure(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty password."""
        hashed = hash_password("TestPassword123")

        assert verify_password("", hashed) is False


class TestPasswordPolicy:
    """Tests for password policy validation.

    Policy requirements (from implementation):
    - Minimum 8 characters
    - At least 1 letter
    - At least 1 number
    """

    def test_validate_password_success(self):
        """Test valid password passes policy."""
        validate_password_policy("TestPassword123")  # Should not raise
        validate_password_policy("abcdefg1")  # lowercase + number
        validate_password_policy("ABCDEFG1")  # uppercase + number

    def test_validate_password_too_short(self):
        """Test short password fails policy."""
        with pytest.raises(PasswordPolicyError, match="8 caracteres"):
            validate_password_policy("Short1")

    def test_validate_password_no_letter(self):
        """Test password without letter fails policy."""
        with pytest.raises(PasswordPolicyError, match="letra"):
            validate_password_policy("12345678")

    def test_validate_password_no_number(self):
        """Test password without number fails policy."""
        with pytest.raises(PasswordPolicyError, match="número"):
            validate_password_policy("TestPassword")


class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_token_returns_string(self):
        """Test token creation returns a string."""
        token = create_token(
            user_id="123",
            email="test@example.com",
            name="Test User",
            role="user",
        )

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_success(self):
        """Test token verification with valid token."""
        token = create_token(
            user_id="123",
            email="test@example.com",
            name="Test User",
            role="admin",
        )

        payload = verify_token(token)

        # Token uses 'sub' for user_id
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["name"] == "Test User"
        assert payload["role"] == "admin"

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        with pytest.raises(UnauthorizedError):
            verify_token("invalid-token")

    def test_extract_user_from_token(self):
        """Test extracting user data from token."""
        token = create_token(
            user_id="123",
            email="test@example.com",
            name="Test User",
            role="user",
        )

        user = extract_user_from_token(token)

        # extract_user_from_token returns a dict
        assert user["user_id"] == "123"
        assert user["email"] == "test@example.com"
        assert user["name"] == "Test User"
        assert user["role"] == "user"


class TestCookieHandling:
    """Tests for cookie handling functions."""

    def test_create_auth_cookie(self):
        """Test auth cookie creation."""
        result = create_auth_cookie("test-token")

        # Returns a dict with Set-Cookie header
        assert "Set-Cookie" in result
        cookie = result["Set-Cookie"]
        assert "auth_token=test-token" in cookie
        assert "HttpOnly" in cookie
        assert "SameSite=" in cookie
        assert "Path=/" in cookie

    def test_create_logout_cookie(self):
        """Test logout cookie creation."""
        result = create_logout_cookie()

        # Returns a dict with Set-Cookie header
        assert "Set-Cookie" in result
        cookie = result["Set-Cookie"]
        assert "auth_token=" in cookie
        assert "Max-Age=0" in cookie

    def test_extract_token_from_cookie_success(self):
        """Test extracting token from cookie header."""
        cookie_header = "auth_token=my-jwt-token; other=value"

        token = extract_token_from_cookie(cookie_header)

        assert token == "my-jwt-token"

    def test_extract_token_from_cookie_missing(self):
        """Test extracting token when auth_token is missing."""
        cookie_header = "other=value; another=thing"

        token = extract_token_from_cookie(cookie_header)

        assert token is None

    def test_extract_token_from_cookie_empty(self):
        """Test extracting token from empty cookie header."""
        token = extract_token_from_cookie("")

        assert token is None

    def test_extract_token_from_cookie_none(self):
        """Test extracting token from None cookie header."""
        token = extract_token_from_cookie(None)

        assert token is None
