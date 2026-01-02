"""Create user endpoint for Controle PGM."""

import azure.functions as func

from core.middleware import (
    create_json_response,
    get_request_body,
    handle_errors,
    require_admin,
)
from models.user import CurrentUser, UserCreate, UserResponse
from services.audit_service import AuditAction, AuditService
from services.user_service import UserService

bp = func.Blueprint()


def _get_client_ip(req: func.HttpRequest) -> str | None:
    """Extract client IP from request headers."""
    return req.headers.get("X-Forwarded-For", req.headers.get("X-Real-IP"))


@bp.route(route="users", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def create_user(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Create a new user.

    POST /api/users

    Request body:
        {
            "email": "usuario@pgm.itajai.sc.gov.br",
            "name": "Nome do Usuário",
            "password": "senha123",
            "role": "user"  // optional, defaults to "user"
        }

    Response (201):
        {
            "id": "...",
            "email": "...",
            "name": "...",
            "role": "user",
            "is_active": true,
            "must_change_password": true,
            "created_at": "...",
            "updated_at": "..."
        }

    Errors:
        400 - Invalid request
        409 - Email already exists
    """
    body = get_request_body(req)
    request_data = UserCreate(**body)

    entity = UserService.create(request_data)
    response = UserResponse.from_entity(entity)

    # Log user creation
    AuditService.log_user_action(
        action=AuditAction.USER_CREATED,
        actor=current_user,
        target_user_id=entity.RowKey,
        target_user_email=entity.Email,
        details={"role": entity.Role, "name": entity.Name},
        ip_address=_get_client_ip(req),
    )

    return create_json_response(response.model_dump(mode="json"), status_code=201)
