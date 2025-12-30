"""Auth functions package for Controle PGM."""

import azure.functions as func

from .change_password import bp as change_password_bp
from .login import bp as login_bp
from .logout import bp as logout_bp
from .me import bp as me_bp

__all__ = ["auth_bp", "change_password_bp", "login_bp", "logout_bp", "me_bp"]

__all__ = ["auth_bp", "change_password_bp", "login_bp", "logout_bp", "me_bp"]

# Create combined blueprint for all auth endpoints
auth_bp = func.Blueprint()

# Register all auth routes
# Note: We need to register each blueprint's functions manually
# because Azure Functions doesn't support nested blueprints directly
