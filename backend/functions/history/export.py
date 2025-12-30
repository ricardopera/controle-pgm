"""History export endpoint for Controle PGM."""

from datetime import datetime

import azure.functions as func

from core.middleware import (
    handle_errors,
    require_auth,
)
from models.user import CurrentUser
from services.history_service import HistoryService

bp = func.Blueprint()


@bp.route(route="history/export", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_auth
def export_history(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Export history to CSV file.

    GET /api/history/export

    Query parameters:
        document_type_code: Filter by document type (optional)
        year: Filter by year (optional)
        user_id: Filter by user ID (optional)
        action: Filter by action type ('generated' or 'corrected') (optional)

    Response (200):
        CSV file download
    """
    # Parse query parameters
    document_type_code = req.params.get("document_type_code")
    year_str = req.params.get("year")
    user_id = req.params.get("user_id")
    action = req.params.get("action")

    # Convert numeric parameters
    year = int(year_str) if year_str else None

    # Validate action
    if action and action not in ("generated", "corrected"):
        action = None

    # Generate CSV
    csv_content = HistoryService.export_csv(
        document_type_code=document_type_code.upper() if document_type_code else None,
        year=year,
        user_id=user_id,
        action=action,
    )

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    parts = ["historico"]
    if document_type_code:
        parts.append(document_type_code.upper())
    if year:
        parts.append(str(year))
    parts.append(timestamp)
    filename = "_".join(parts) + ".csv"

    return func.HttpResponse(
        body=csv_content.encode("utf-8-sig"),  # BOM for Excel compatibility
        status_code=200,
        mimetype="text/csv",
        charset="utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )
