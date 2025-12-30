"""Delete (deactivate) user endpoint for Controle PGM."""

import azure.functions as func

from backend.core.exceptions import NotFoundError
from backend.core.middleware import (
    create_json_response,
    handle_errors,
    require_admin,
)
from backend.models.user import CurrentUser
from backend.services.user_service import UserService

bp = func.Blueprint()


@bp.route(route="users/{user_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def delete_user(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Deactivate a user (soft delete).

    DELETE /api/users/{user_id}

    Response (200):
        {
            "success": true,
            "message": "Usuário desativado com sucesso"
        }

    Errors:
        400 - Cannot deactivate last admin
        404 - User not found
    """
    user_id = req.route_params.get("user_id")

    # Check if user exists
    user = UserService.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    # Deactivate user (handles admin protection internally)
    UserService.deactivate(user_id, current_user.user_id)

    return create_json_response(
        {"success": True, "message": "Usuário desativado com sucesso"}, status_code=200
    )
