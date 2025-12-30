"""History list endpoint for Controle PGM."""

import azure.functions as func

from core.middleware import (
    create_json_response,
    handle_errors,
    require_auth,
)
from models.number_log import HistoryFilter
from models.user import CurrentUser
from services.history_service import HistoryService

bp = func.Blueprint()


@bp.route(route="history", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_auth
def list_history(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """List number generation history with filters.

    GET /api/history

    Query parameters:
        document_type_code: Filter by document type (optional)
        year: Filter by year (optional)
        user_id: Filter by user ID (optional)
        action: Filter by action type ('generated' or 'corrected') (optional)
        page: Page number (default: 1)
        page_size: Items per page (default: 50, max: 100)

    Response (200):
        {
            "items": [...],
            "total": 150,
            "page": 1,
            "page_size": 50,
            "total_pages": 3
        }
    """
    # Parse query parameters
    document_type_code = req.params.get("document_type_code")
    year_str = req.params.get("year")
    user_id = req.params.get("user_id")
    action = req.params.get("action")
    page_str = req.params.get("page", "1")
    page_size_str = req.params.get("page_size", "50")

    # Convert numeric parameters
    year = int(year_str) if year_str else None
    page = int(page_str) if page_str.isdigit() else 1
    page_size = int(page_size_str) if page_size_str.isdigit() else 50

    # Validate action
    if action and action not in ("generated", "corrected"):
        action = None

    # Create filter
    filters = HistoryFilter(
        document_type_code=document_type_code.upper() if document_type_code else None,
        year=year,
        user_id=user_id,
        action=action,  # type: ignore
        page=page,
        page_size=min(page_size, 100),  # Cap at 100
    )

    result = HistoryService.list_history(filters)

    return create_json_response(
        {
            "items": [item.model_dump(mode="json") for item in result.items],
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
        },
        status_code=200,
    )
