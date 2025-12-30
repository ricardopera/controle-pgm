"""Login endpoint for Controle PGM."""

import azure.functions as func

from core.auth import create_auth_cookie, create_token
from core.middleware import create_json_response, get_request_body, handle_errors
from models.user import LoginRequest, LoginResponse
from services.user_service import UserService

# Create blueprint for auth functions
bp = func.Blueprint()


@bp.route(route="auth/login", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
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

    # Verify credentials
    user = UserService.verify_credentials(login_data.email, login_data.password)

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
    response.headers["Set-Cookie"] = create_auth_cookie(token)

    return response
