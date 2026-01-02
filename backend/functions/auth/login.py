"""Login endpoint for Controle PGM."""

import azure.functions as func

from core.auth import create_auth_cookie, create_token
from core.middleware import create_json_response, get_request_body, handle_errors
from core.rate_limit import rate_limit
from models.user import LoginRequest, LoginResponse
from services.audit_service import AuditAction, AuditService
from services.user_service import UserService

# Create blueprint for auth functions
bp = func.Blueprint()


def _get_client_ip(req: func.HttpRequest) -> str | None:
    """Extract client IP from request headers."""
    return req.headers.get("X-Forwarded-For", req.headers.get("X-Real-IP"))


@bp.route(route="auth/login", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@rate_limit(max_requests=5, window_minutes=1)  # Strict rate limit for login attempts
def login(req: func.HttpRequest) -> func.HttpResponse:
    """Handle user login.

    POST /api/auth/login

    Request body:
        {
            "email": "user@example.com",
            "password": "password123"
        }

    Response (200):
        {
            "user_id": "uuid",
            "email": "user@example.com",
            "name": "User Name",
            "role": "user",
            "must_change_password": false
        }

    Errors:
        401 - Invalid credentials
        403 - User inactive
    """
    # Parse and validate request body
    body = get_request_body(req)
    login_data = LoginRequest(**body)
    client_ip = _get_client_ip(req)

    try:
        # Verify credentials
        user = UserService.verify_credentials(login_data.email, login_data.password)

        # Log successful login
        AuditService.log(
            action=AuditAction.LOGIN_SUCCESS,
            actor_id=user.RowKey,
            actor_email=user.Email,
            ip_address=client_ip,
        )

        # Create JWT token
        token = create_token(
            user_id=user.RowKey,
            email=user.Email,
            name=user.Name,
            role=user.Role,
            must_change_password=user.MustChangePassword,
        )

        # Create response
        response_data = LoginResponse(
            user_id=user.RowKey,
            email=user.Email,
            name=user.Name,
            role=user.Role,
            must_change_password=user.MustChangePassword,
        )

        # Return response with auth cookie
        response = create_json_response(response_data.model_dump(), status_code=200)
        cookie_headers = create_auth_cookie(token)
        response.headers["Set-Cookie"] = cookie_headers["Set-Cookie"]

        return response

    except Exception as e:
        # Log failed login attempt
        AuditService.log(
            action=AuditAction.LOGIN_FAILED,
            actor_id=None,
            actor_email=login_data.email,
            details={"reason": str(e)},
            ip_address=client_ip,
        )
        raise
