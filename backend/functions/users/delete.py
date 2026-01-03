"""Delete (deactivate) user endpoint for Controle PGM."""

import azure.functions as func

from core.exceptions import BadRequestError, NotFoundError
from core.middleware import (
    create_json_response,
    handle_errors,
    require_admin,
)
from core.security import is_valid_uuid
from models.user import CurrentUser
from services.audit_service import AuditAction, AuditService
from services.user_service import UserService

bp = func.Blueprint()


@bp.route(route="users/{user_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def delete_user(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Delete a user permanently (Hard Delete).

    DELETE /api/users/{user_id}

    Response (200):
        {
            "success": true,
            "message": "Usuário excluído com sucesso"
        }

    Errors:
        400 - Invalid user ID or cannot delete last admin
        404 - User not found
    """
    user_id = req.route_params.get("user_id")

    if not is_valid_uuid(user_id):
        raise BadRequestError("ID de usuário inválido")

    # Check if user exists
    user = UserService.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    # Delete user permanently (handles admin protection internally)
    UserService.delete_permanently(user_id, current_user["user_id"])

    # Log user deletion
    AuditService.log_user_action(
        action=AuditAction.USER_DEACTIVATED,  # Reuse or add USER_DELETED
        actor=current_user,
        target_user_id=user_id,
        target_user_email=user.Email,
        ip_address=req.headers.get("X-Forwarded-For"),
    )

    return create_json_response(
        {"success": True, "message": "Usuário excluído com sucesso"}, status_code=200
    )
