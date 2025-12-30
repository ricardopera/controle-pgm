"""List users endpoint for Controle PGM."""

import azure.functions as func

from core.middleware import (
    create_json_response,
    handle_errors,
    require_admin,
)
from models.user import CurrentUser, UserResponse
from services.user_service import UserService

bp = func.Blueprint()


@bp.route(route="users", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def list_users(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """List all users.

    GET /api/users

    Response (200):
        [
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
        ]
    """
    entities = UserService.list_all()

    # Sort by name
    entities.sort(key=lambda x: x.Name.lower())

    response = [UserResponse.from_entity(e).model_dump(mode="json") for e in entities]

    return create_json_response(response, status_code=200)
