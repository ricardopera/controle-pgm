"""List document types endpoint for Controle PGM."""

import azure.functions as func

from core.middleware import create_json_response, handle_errors, require_auth
from models.document_type import DocumentTypeListResponse, DocumentTypeResponse
from models.user import CurrentUser
from services.document_type_service import DocumentTypeService

bp = func.Blueprint()


@bp.route(route="document-types", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_auth
def list_document_types(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """List all active document types.

    GET /api/document-types

    Query parameters:
        all (optional): If "true", include inactive types (admin only)

    Response (200):
        {
            "items": [
                {
                    "id": "uuid",
                    "code": "OF",
                    "name": "Ofício",
                    "is_active": true,
                    "created_at": "2025-01-15T10:00:00Z",
                    "updated_at": "2025-01-15T10:00:00Z"
                },
                ...
            ],
            "total": 10
        }
    """
    # Check if admin wants all document types
    include_all = req.params.get("all", "").lower() == "true"

    if include_all and current_user["role"] == "admin":
        doc_types = DocumentTypeService.list_all()
    else:
        doc_types = DocumentTypeService.list_active()

    items = [DocumentTypeResponse.from_entity(dt) for dt in doc_types]

    response = DocumentTypeListResponse(
        items=items,
        total=len(items),
    )

    return create_json_response(response.model_dump(mode="json"), status_code=200)
