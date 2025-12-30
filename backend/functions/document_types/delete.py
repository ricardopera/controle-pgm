"""Delete (deactivate) document type endpoint for Controle PGM."""

import azure.functions as func

from core.middleware import (
    create_json_response,
    handle_errors,
    require_admin,
)
from models.document_type import DocumentTypeResponse
from models.user import CurrentUser
from services.document_type_service import DocumentTypeService

bp = func.Blueprint()


@bp.route(
    route="document-types/{doc_type_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS
)
@handle_errors
@require_admin
def delete_document_type(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Deactivate a document type (soft delete).

    DELETE /api/document-types/{doc_type_id}

    Note: This performs a soft delete by setting is_active to false.
    Document types are not physically deleted to maintain data integrity.

    Response (200):
        {
            "id": "...",
            "code": "OF",
            "name": "Ofício",
            "is_active": false,
            "created_at": "...",
            "updated_at": "..."
        }

    Errors:
        404 - Document type not found
    """
    doc_type_id = req.route_params.get("doc_type_id")

    entity = DocumentTypeService.deactivate(doc_type_id)
    response = DocumentTypeResponse.from_entity(entity)

    return create_json_response(response.model_dump(mode="json"), status_code=200)
