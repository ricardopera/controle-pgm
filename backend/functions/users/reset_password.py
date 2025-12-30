"""Reset user password endpoint for Controle PGM."""

import azure.functions as func

from core.exceptions import NotFoundError
from core.middleware import (
    create_json_response,
    handle_errors,
    require_admin,
)
from models.user import CurrentUser
from services.user_service import UserService

bp = func.Blueprint()


@bp.route(
    route="users/{user_id}/reset-password", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS
)
@handle_errors
@require_admin
def reset_user_password(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Reset a user's password to a temporary one.

    POST /api/users/{user_id}/reset-password

    Response (200):
        {
            "success": true,
            "message": "Senha redefinida com sucesso",
            "temporary_password": "abc123XYZ"
        }

    Errors:
        404 - User not found
    """
    user_id = req.route_params.get("user_id")

    # Check if user exists
    user = UserService.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    # Reset password and get temporary one
    temp_password = UserService.reset_password(user_id)

    return create_json_response(
        {
            "success": True,
            "message": "Senha redefinida com sucesso",
            "temporary_password": temp_password,
        },
        status_code=200,
    )
