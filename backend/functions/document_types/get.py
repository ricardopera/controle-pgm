"""Get document type endpoint for Controle PGM."""

import azure.functions as func

from core.exceptions import NotFoundError
from core.middleware import (
    create_json_response,
    handle_errors,
    require_auth,
)
from models.document_type import DocumentTypeResponse
from models.user import CurrentUser
from services.document_type_service import DocumentTypeService

bp = func.Blueprint()


@bp.route(
    route="document-types/{doc_type_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS
)
@handle_errors
@require_auth
def get_document_type(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Get a document type by ID.

    GET /api/document-types/{doc_type_id}

    Response (200):
        {
            "id": "...",
            "code": "OF",
            "name": "Ofício",
            "is_active": true,
            "created_at": "...",
            "updated_at": "..."
        }

    Errors:
        404 - Document type not found
    """
    doc_type_id = req.route_params.get("doc_type_id")

    entity = DocumentTypeService.get_by_id(doc_type_id)
    if not entity:
        raise NotFoundError("Tipo de documento não encontrado")

    response = DocumentTypeResponse.from_entity(entity)

    return create_json_response(response.model_dump(mode="json"), status_code=200)
