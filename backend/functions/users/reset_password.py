"""Reset user password endpoint for Controle PGM."""

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
        400 - Invalid user ID format
        404 - User not found
    """
    user_id = req.route_params.get("user_id")
    
    if not is_valid_uuid(user_id):
        raise BadRequestError("ID de usuário inválido")

    # Check if user exists
    user = UserService.get_by_id(user_id)
    if not user:
        raise NotFoundError("Usuário não encontrado")

    # Reset password and get temporary one
    temp_password = UserService.reset_password(user_id)

    # Log password reset
    AuditService.log_user_action(
        action=AuditAction.USER_PASSWORD_RESET,
        actor=current_user,
        target_user_id=user_id,
        target_user_email=user.Email,
        ip_address=req.headers.get("X-Forwarded-For"),
    )

    return create_json_response(
        {
            "success": True,
            "message": "Senha redefinida com sucesso",
            "temporary_password": temp_password,
        },
        status_code=200,
    )
