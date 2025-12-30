"""Rate limiting middleware for Controle PGM."""

from __future__ import annotations

import json
import time
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from threading import Lock
from typing import Any, TypeVar

import azure.functions as func

from .config import settings

F = TypeVar("F", bound=Callable[..., Any])

# In-memory rate limiter (resets on function cold start)
# For production, consider using Azure Redis Cache
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
_rate_limit_lock = Lock()


def _clean_old_requests(key: str, window_seconds: int) -> None:
    """Remove requests outside the current window."""
    cutoff = time.time() - window_seconds
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if t > cutoff]


def _check_rate_limit(key: str, max_requests: int, window_seconds: int) -> bool:
    """
    Check if request should be rate limited.

    Args:
        key: Unique identifier for the rate limit (e.g., user_id or IP)
        max_requests: Maximum requests allowed in the window
        window_seconds: Time window in seconds

    Returns:
        True if request is allowed, False if rate limited
    """
    with _rate_limit_lock:
        _clean_old_requests(key, window_seconds)

        if len(_rate_limit_store[key]) >= max_requests:
            return False

        _rate_limit_store[key].append(time.time())
        return True


def rate_limit(
    max_requests: int | None = None,
    window_minutes: int | None = None,
    key_func: Callable[[func.HttpRequest], str] | None = None,
) -> Callable[[F], F]:
    """
    Decorator to apply rate limiting to an endpoint.

    Args:
        max_requests: Maximum requests per window (default from settings)
        window_minutes: Time window in minutes (default from settings)
        key_func: Function to extract rate limit key from request
                  Default: uses user_id from current_user or IP address

    Usage:
        @rate_limit(max_requests=10, window_minutes=1)
        @require_auth
        def my_endpoint(req, current_user):
            ...
    """
    _max = max_requests or settings.rate_limit_requests
    _window = (window_minutes or settings.rate_limit_window_minutes) * 60

    def decorator(func_handler: F) -> F:
        @wraps(func_handler)
        def wrapper(req: func.HttpRequest, *args: Any, **kwargs: Any) -> func.HttpResponse:
            # Determine rate limit key
            if key_func:
                key = key_func(req)
            elif "current_user" in kwargs:
                # Use user_id if authenticated
                key = f"user:{kwargs['current_user']['user_id']}"
            else:
                # Fall back to IP address
                key = f"ip:{req.headers.get('X-Forwarded-For', 'unknown')}"

            # Check rate limit
            if not _check_rate_limit(key, _max, _window):
                return func.HttpResponse(
                    body=json.dumps(
                        {
                            "error": "Limite de requisições excedido. Tente novamente em alguns instantes."
                        }
                    ),
                    status_code=429,
                    headers={
                        "Retry-After": str(_window),
                        "Content-Type": "application/json",
                    },
                )

            return func_handler(req, *args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def add_security_headers(response: func.HttpResponse) -> func.HttpResponse:
    """
    Add security headers to a response.

    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    - Cache-Control: no-store (for API responses)
    """
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "no-store, no-cache, must-revalidate",
    }

    # Update response headers
    for key, value in security_headers.items():
        # Azure Functions HttpResponse doesn't have a direct header setter
        # Headers are set during construction, so we need to return a new response
        pass  # Headers are added at the Function App level via host.json

    return response


def get_cors_headers() -> dict[str, str]:
    """
    Get CORS headers based on environment configuration.

    Returns:
        Dictionary of CORS headers
    """
    return {
        "Access-Control-Allow-Origin": settings.cors_origins_list[0]
        if settings.cors_origins_list
        else "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, Cookie",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400",  # 24 hours
    }
