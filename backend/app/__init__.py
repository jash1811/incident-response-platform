from flask import Flask, jsonify
from flasgger import Swagger
from app.extensions import db, jwt, cors
from app.config.config import get_config


SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/",
    "info": {
        "title": "Incident Response Platform API",
        "description": "Multi-tenant Incident Response Platform REST API",
        "version": "1.0.0",
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT token. Format: Bearer <token>",
        }
    },
}


def create_app():
    app = Flask(__name__)
    cfg = get_config()
    app.config.from_object(cfg)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Swagger
    Swagger(app, config=SWAGGER_CONFIG, merge=True)

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import users_bp
    from app.routes.incident_routes import incidents_bp
    from app.routes.comment_routes import comments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(comments_bp)

    # Dashboard stats endpoint
    from app.routes.dashboard_routes import dashboard_bp
    app.register_blueprint(dashboard_bp)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token is required"}), 401

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    # Health check
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "incident-platform"}), 200

    return app
