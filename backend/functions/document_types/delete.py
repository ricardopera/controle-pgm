"""Delete (deactivate) document type endpoint for Controle PGM."""

import azure.functions as func

from core.middleware import (
    create_json_response,
    handle_errors,
    require_admin,
)
from models.user import CurrentUser
from services.document_type_service import DocumentTypeService

bp = func.Blueprint()


@bp.route(
    route="document-types/{doc_type_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS
)
@handle_errors
@require_admin
def delete_document_type(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Delete a document type permanently (Hard Delete).

    DELETE /api/document-types/{doc_type_id}

    Response (200):
        {
            "success": true,
            "message": "Tipo de documento excluído com sucesso"
        }

    Errors:
        404 - Document type not found
        409 - Document type has generated numbers
    """
    doc_type_id = req.route_params.get("doc_type_id")

    DocumentTypeService.delete_permanently(doc_type_id)

    return create_json_response(
        {"success": True, "message": "Tipo de documento excluído com sucesso"}, status_code=200
    )
