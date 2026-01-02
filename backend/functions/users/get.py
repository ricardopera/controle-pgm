"""Get user endpoint for Controle PGM."""

import azure.functions as func

from core.exceptions import BadRequestError, NotFoundError
from core.middleware import (
    create_json_response,
    handle_errors,
    require_admin,
)
from core.security import is_valid_uuid
from models.user import CurrentUser, UserResponse
from services.user_service import UserService

bp = func.Blueprint()


@bp.route(route="users/{user_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def get_user(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Get a user by ID.

    GET /api/users/{user_id}

    Response (200):
        {
            "id": "...",
            "email": "...",
            "name": "...",
            "role": "admin|user",
            "is_active": true,
            "must_change_password": false,
            "created_at": "...",
            "updated_at": "..."
        }

    Errors:
        400 - Invalid user ID format
        404 - User not found
    """
    user_id = req.route_params.get("user_id")

    if not is_valid_uuid(user_id):
        raise BadRequestError("ID de usuário inválido")

    entity = UserService.get_by_id(user_id)
    if not entity:
        raise NotFoundError("Usuário não encontrado")

    response = UserResponse.from_entity(entity)

    return create_json_response(response.model_dump(mode="json"), status_code=200)
