"""Authentication middleware decorators for Azure Functions."""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

import azure.functions as func

from core.auth import extract_token_from_cookie, extract_user_from_token
from core.exceptions import ControlePGMError, ForbiddenError, UnauthorizedError

F = TypeVar("F", bound=Callable[..., Any])


def create_error_response(error: ControlePGMError) -> func.HttpResponse:
    """Create an HTTP error response from an exception."""
    return func.HttpResponse(
        body=json.dumps({"error": error.message}),
        status_code=error.status_code,
        mimetype="application/json",
    )


def create_json_response(
    data: dict[str, Any] | list[Any],
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> func.HttpResponse:
    """Create a JSON HTTP response."""
    response_headers = {"Content-Type": "application/json"}
    if headers:
        response_headers.update(headers)

    return func.HttpResponse(
        body=json.dumps(data, default=str),
        status_code=status_code,
        headers=response_headers,
        mimetype="application/json",
    )


def require_auth(func_handler: F) -> F:
    """
    Decorator to require authentication for an Azure Function.

    Extracts user from JWT token in cookie and passes to handler.
    Handler receives 'current_user' as keyword argument.

    Usage:
        @require_auth
        def my_function(req: func.HttpRequest, current_user: dict) -> func.HttpResponse:
            ...
    """

    @wraps(func_handler)
    def wrapper(req: func.HttpRequest, *args: Any, **kwargs: Any) -> func.HttpResponse:
        try:
            # Extract token from cookie
            cookie_header = req.headers.get("Cookie")
            token = extract_token_from_cookie(cookie_header)

            if not token:
                raise UnauthorizedError()

            # Verify token and extract user
            current_user = extract_user_from_token(token)

            # Pass user to handler
            return func_handler(req, *args, current_user=current_user, **kwargs)

        except ControlePGMError as e:
            return create_error_response(e)

    return wrapper  # type: ignore


def require_admin(func_handler: F) -> F:
    """
    Decorator to require admin role for an Azure Function.

    Must be used after @require_auth or combined.
    Handler receives 'current_user' as keyword argument.

    Usage:
        @require_admin
        def admin_only_function(req: func.HttpRequest, current_user: dict) -> func.HttpResponse:
            ...
    """

    @wraps(func_handler)
    def wrapper(req: func.HttpRequest, *args: Any, **kwargs: Any) -> func.HttpResponse:
        try:
            # Extract token from cookie
            cookie_header = req.headers.get("Cookie")
            token = extract_token_from_cookie(cookie_header)

            if not token:
                raise UnauthorizedError()

            # Verify token and extract user
            current_user = extract_user_from_token(token)

            # Check admin role
            if current_user.get("role") != "admin":
                raise ForbiddenError("Acesso restrito a administradores")

            # Pass user to handler
            return func_handler(req, *args, current_user=current_user, **kwargs)

        except ControlePGMError as e:
            return create_error_response(e)

    return wrapper  # type: ignore


def handle_errors(func_handler: F) -> F:
    """
    Decorator to handle exceptions and return appropriate HTTP responses.

    Catches ControlePGMError exceptions and returns JSON error responses.
    Catches unexpected exceptions and returns 500 error.

    Usage:
        @handle_errors
        def my_function(req: func.HttpRequest) -> func.HttpResponse:
            ...
    """

    @wraps(func_handler)
    def wrapper(req: func.HttpRequest, *args: Any, **kwargs: Any) -> func.HttpResponse:
        try:
            return func_handler(req, *args, **kwargs)
        except ControlePGMError as e:
            return create_error_response(e)
        except Exception:
            # Log unexpected errors in production
            error_message = "Erro interno do servidor"
            return func.HttpResponse(
                body=json.dumps({"error": error_message}),
                status_code=500,
                mimetype="application/json",
            )

    return wrapper  # type: ignore


def get_request_body(req: func.HttpRequest) -> dict[str, Any]:
    """
    Parse JSON body from request.

    Args:
        req: HTTP request.

    Returns:
        Parsed JSON body as dictionary.

    Raises:
        BadRequestError: If body is not valid JSON.
    """
    from core.exceptions import BadRequestError

    try:
        body = req.get_json()
        if not isinstance(body, dict):
            raise BadRequestError("Corpo da requisição deve ser um objeto JSON")
        return body
    except ValueError:
        raise BadRequestError("Corpo da requisição deve ser JSON válido")
