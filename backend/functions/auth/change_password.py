"""Change password endpoint for Controle PGM."""

import azure.functions as func

from backend.core.auth import create_auth_cookie, create_token, validate_password_policy
from backend.core.middleware import (
    create_json_response,
    get_request_body,
    handle_errors,
    require_auth,
)
from backend.models.user import ChangePasswordRequest, CurrentUser
from backend.services.user_service import UserService

# Create blueprint for change password
bp = func.Blueprint()


@bp.route(route="auth/change-password", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_auth
def change_password(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Change current user's password.

    POST /api/auth/change-password

    Request body:
        {
            "current_password": "currentPassword123",
            "new_password": "newPassword456"
        }

    Response (200):
        {"message": "Password changed successfully"}

    Errors:
        400 - Password does not meet policy
        401 - Current password incorrect
    """
    # Parse and validate request body
    body = get_request_body(req)
    change_data = ChangePasswordRequest(**body)

    # Validate new password policy
    validate_password_policy(change_data.new_password)

    # Change password
    UserService.change_password(
        user_id=current_user.user_id,
        current_password=change_data.current_password,
        new_password=change_data.new_password,
    )

    # Get updated user
    user = UserService.get_by_id(current_user.user_id)

    # Create new token without must_change_password flag
    token = create_token(
        user_id=user.RowKey,
        email=user.Email,
        name=user.Name,
        role=user.Role,
        must_change_password=False,
    )

    # Return response with updated cookie
    response = create_json_response({"message": "Senha alterada com sucesso"}, status_code=200)
    response.headers["Set-Cookie"] = create_auth_cookie(token)

    return response
