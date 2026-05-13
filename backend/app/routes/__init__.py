from app.routes.auth_routes import auth_bp
from app.routes.user_routes import users_bp
from app.routes.incident_routes import incidents_bp
from app.routes.comment_routes import comments_bp

__all__ = ["auth_bp", "users_bp", "incidents_bp", "comments_bp"]
