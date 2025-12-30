"""Core module for Controle PGM backend."""

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
from core.config import Settings, get_settings, settings
from core.exceptions import (
    BadRequestError,
    ConflictError,
    ControlePGMError,
    ForbiddenError,
    InvalidCredentialsError,
    NotFoundError,
    PasswordPolicyError,
    SequenceGenerationError,
    TokenExpiredError,
    UnauthorizedError,
    UserDeactivatedError,
    ValidationError,
)
from core.middleware import (
    create_error_response,
    create_json_response,
    get_request_body,
    handle_errors,
    require_admin,
    require_auth,
)
from core.tables import (
    TABLE_DOCUMENT_TYPES,
    TABLE_NUMBER_LOGS,
    TABLE_SEQUENCES,
    TABLE_USERS,
    get_document_types_table,
    get_number_logs_table,
    get_sequences_table,
    get_table_client,
    get_table_service_client,
    get_users_table,
)

__all__ = [
    # Config
    "Settings",
    "get_settings",
    "settings",
    # Auth
    "hash_password",
    "verify_password",
    "validate_password_policy",
    "create_token",
    "verify_token",
    "extract_user_from_token",
    "create_auth_cookie",
    "create_logout_cookie",
    "extract_token_from_cookie",
    # Exceptions
    "ControlePGMError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "BadRequestError",
    "ConflictError",
    "ValidationError",
    "PasswordPolicyError",
    "UserDeactivatedError",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "SequenceGenerationError",
    # Middleware
    "require_auth",
    "require_admin",
    "handle_errors",
    "create_error_response",
    "create_json_response",
    "get_request_body",
    # Tables
    "TABLE_USERS",
    "TABLE_DOCUMENT_TYPES",
    "TABLE_SEQUENCES",
    "TABLE_NUMBER_LOGS",
    "get_table_service_client",
    "get_table_client",
    "get_users_table",
    "get_document_types_table",
    "get_sequences_table",
    "get_number_logs_table",
]
