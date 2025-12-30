"""Logout endpoint for Controle PGM."""

import azure.functions as func

from backend.core.auth import create_logout_cookie
from backend.core.middleware import create_json_response, handle_errors

# Create blueprint for logout
bp = func.Blueprint()


@bp.route(route="auth/logout", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
def logout(req: func.HttpRequest) -> func.HttpResponse:
    """Handle user logout.

    POST /api/auth/logout

    Response (200):
        {"message": "Logout successful"}

    Note: Clears the auth cookie.
    """
    response = create_json_response({"message": "Logout realizado com sucesso"}, status_code=200)
    response.headers["Set-Cookie"] = create_logout_cookie()

    return response
