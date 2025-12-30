"""Generate number endpoint for Controle PGM."""

import azure.functions as func

from core.middleware import (
    create_json_response,
    get_request_body,
    handle_errors,
    require_auth,
)
from core.rate_limit import rate_limit
from models.sequence import GenerateNumberRequest, GenerateNumberResponse
from models.user import CurrentUser
from services.number_service import NumberService

bp = func.Blueprint()


@bp.route(route="numbers/generate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@rate_limit(max_requests=30, window_minutes=1)  # 30 requests per minute per user
@require_auth
def generate_number(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
    """Generate next document number.

    POST /api/numbers/generate

    Request body:
        {
            "document_type_code": "OF",
            "year": 2025
        }

    Response (200):
        {
            "number": 43,
            "document_type_code": "OF",
            "year": 2025,
            "formatted": "OF 0043/2025"
        }

    Errors:
        400 - Invalid request
        404 - Document type not found
        500 - Generation failed
    """
    body = get_request_body(req)
    request_data = GenerateNumberRequest(**body)

    number, formatted, document_type_name = NumberService.generate_number(
        document_type_code=request_data.document_type_code.upper(),
        year=request_data.year,
        user=current_user,
    )

    response = GenerateNumberResponse(
        number=number,
        document_type_code=request_data.document_type_code.upper(),
        document_type_name=document_type_name,
        year=request_data.year,
        formatted=formatted,
    )

    return create_json_response(response.model_dump(), status_code=200)
