"""Me endpoint for Controle PGM - returns current user info."""

import azure.functions as func

from backend.core.middleware import create_json_response, handle_errors, require_auth
from backend.models.user import CurrentUser

# Create blueprint for me endpoint
bp = func.Blueprint()


@bp.route(route="auth/me", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_auth
def me(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Get current authenticated user info.

    GET /api/auth/me

    Response (200):
        {
            "user_id": "uuid",
            "email": "user@example.com",
            "name": "User Name",
            "role": "user",
            "must_change_password": false
        }

    Errors:
        401 - Not authenticated
    """
    return create_json_response(
        {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "must_change_password": current_user.must_change_password,
        }
    )
