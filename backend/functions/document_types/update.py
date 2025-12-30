"""Update document type endpoint for Controle PGM."""

import azure.functions as func

from backend.core.middleware import (
    create_json_response,
    get_request_body,
    handle_errors,
    require_admin,
)
from backend.models.document_type import DocumentTypeResponse, DocumentTypeUpdate
from backend.models.user import CurrentUser
from backend.services.document_type_service import DocumentTypeService

bp = func.Blueprint()


@bp.route(
    route="document-types/{doc_type_id}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS
)
@handle_errors
@require_admin
def update_document_type(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Update a document type.

    PUT /api/document-types/{doc_type_id}

    Request body:
        {
            "name": "Novo Nome",
            "is_active": false
        }

    Response (200):
        {
            "id": "...",
            "code": "OF",
            "name": "Novo Nome",
            "is_active": false,
            "created_at": "...",
            "updated_at": "..."
        }

    Errors:
        400 - Invalid request
        404 - Document type not found
    """
    doc_type_id = req.route_params.get("doc_type_id")
    body = get_request_body(req)
    request_data = DocumentTypeUpdate(**body)

    entity = DocumentTypeService.update(doc_type_id, request_data)
    response = DocumentTypeResponse.from_entity(entity)

    return create_json_response(response.model_dump(mode="json"), status_code=200)
