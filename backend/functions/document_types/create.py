"""Create document type endpoint for Controle PGM."""

import azure.functions as func

from backend.core.middleware import (
    create_json_response,
    get_request_body,
    handle_errors,
    require_admin,
)
from backend.models.document_type import DocumentTypeCreate, DocumentTypeResponse
from backend.models.user import CurrentUser
from backend.services.document_type_service import DocumentTypeService

bp = func.Blueprint()


@bp.route(route="document-types", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def create_document_type(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Create a new document type.

    POST /api/document-types

    Request body:
        {
            "code": "PAR",
            "name": "Parecer"
        }

    Response (201):
        {
            "id": "...",
            "code": "PAR",
            "name": "Parecer",
            "is_active": true,
            "created_at": "...",
            "updated_at": "..."
        }

    Errors:
        400 - Invalid request
        409 - Code already exists
    """
    body = get_request_body(req)
    request_data = DocumentTypeCreate(**body)

    entity = DocumentTypeService.create(request_data)
    response = DocumentTypeResponse.from_entity(entity)

    return create_json_response(response.model_dump(mode="json"), status_code=201)
