"""Update user endpoint for Controle PGM."""

import azure.functions as func

from backend.core.exceptions import NotFoundError
from backend.core.middleware import (
    create_json_response,
    get_request_body,
    handle_errors,
    require_admin,
)
from backend.models.user import CurrentUser, UserResponse
from backend.services.user_service import UserService

bp = func.Blueprint()


@bp.route(route="users/{user_id}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def update_user(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Update a user.

    PUT /api/users/{user_id}

    Request body:
        {
            "name": "Novo Nome",
            "role": "admin",
            "is_active": true
        }

    Response (200):
        {
            "id": "...",
            "email": "...",
            "name": "Novo Nome",
            "role": "admin",
            "is_active": true,
            "must_change_password": false,
            "created_at": "...",
            "updated_at": "..."
        }

    Errors:
        400 - Invalid request
        403 - Forbidden (e.g., removing last admin)
        404 - User not found
    """
    user_id = req.route_params.get("user_id")
    body = get_request_body(req)

    # Get user first to check if exists
    user = UserService.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    # Build update dict from allowed fields
    updates = {}

    if "name" in body:
        updates["Name"] = body["name"]

    if "role" in body:
        # Check if trying to remove admin role
        if body["role"] == "user" and user.Role == "admin":
            # Use the remove_admin_role method for safety
            UserService.remove_admin_role(user_id, current_user.user_id)
            updates = {}  # Already updated
        elif body["role"] == "admin" and user.Role == "user":
            updates["Role"] = "admin"

    if "is_active" in body:
        if not body["is_active"] and user.IsActive:
            # Use deactivate method for safety
            UserService.deactivate(user_id, current_user.user_id)
            updates = {}  # Already updated
        elif body["is_active"] and not user.IsActive:
            updates["IsActive"] = True

    # Apply remaining updates if any
    if updates:
        UserService.update(user_id, updates)

    # Get fresh user data
    entity = UserService.get_by_id(user_id)
    response = UserResponse.from_entity(entity)

    return create_json_response(response.model_dump(mode="json"), status_code=200)
