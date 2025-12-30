"""Azure Functions v4 entry point for Controle PGM API."""

import azure.functions as func

from backend.functions.auth.change_password import bp as change_password_bp

# Import auth blueprints
from backend.functions.auth.login import bp as login_bp
from backend.functions.auth.logout import bp as logout_bp
from backend.functions.auth.me import bp as me_bp
from backend.functions.document_types.create import bp as create_document_type_bp
from backend.functions.document_types.delete import bp as delete_document_type_bp
from backend.functions.document_types.get import bp as get_document_type_bp

# Import document types blueprints
from backend.functions.document_types.list import bp as list_document_types_bp
from backend.functions.document_types.update import bp as update_document_type_bp
from backend.functions.history.export import bp as export_history_bp

# Import history blueprints
from backend.functions.history.list import bp as list_history_bp

# Import numbers blueprint
from backend.functions.numbers.generate import bp as generate_number_bp
from backend.functions.users.create import bp as create_user_bp
from backend.functions.users.delete import bp as delete_user_bp
from backend.functions.users.get import bp as get_user_bp

# Import users blueprints
from backend.functions.users.list import bp as list_users_bp
from backend.functions.users.reset_password import bp as reset_password_bp
from backend.functions.users.update import bp as update_user_bp

# Create the main Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# =============================================================================
# Health Check Endpoint
# =============================================================================


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint for monitoring."""
    import json

    return func.HttpResponse(
        body=json.dumps({"status": "healthy", "service": "controle-pgm-api"}),
        status_code=200,
        mimetype="application/json",
    )


# =============================================================================
# Blueprint Registration
# =============================================================================

# Auth endpoints
app.register_functions(login_bp)
app.register_functions(logout_bp)
app.register_functions(me_bp)
app.register_functions(change_password_bp)

# Numbers endpoints
app.register_functions(generate_number_bp)

# Document types endpoints
app.register_functions(list_document_types_bp)
app.register_functions(create_document_type_bp)
app.register_functions(get_document_type_bp)
app.register_functions(update_document_type_bp)
app.register_functions(delete_document_type_bp)

# History endpoints
app.register_functions(list_history_bp)
app.register_functions(export_history_bp)

# Users endpoints
app.register_functions(list_users_bp)
app.register_functions(create_user_bp)
app.register_functions(get_user_bp)
app.register_functions(update_user_bp)
app.register_functions(delete_user_bp)
app.register_functions(reset_password_bp)
