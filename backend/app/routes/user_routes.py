from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.user import User
from app.schemas.validators import validate_create_user
from app.schemas.serializers import serialize_user
from app.middleware.auth_middleware import (
    tenant_required, admin_required,
    get_current_tenant_id,
)
from app.utils.errors import handle_validation_error, handle_not_found
from app.utils.pagination import paginate_query

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("", methods=["GET"])
@jwt_required()
@tenant_required
def list_users():
    """
    List all users in the current tenant.
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
      - in: query
        name: per_page
        type: integer
    responses:
      200:
        description: List of users
    """
    tenant_id = get_current_tenant_id()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    query = User.query.filter_by(tenant_id=tenant_id).order_by(User.created_at.desc())
    result = paginate_query(query, page, per_page)

    return jsonify({
        "users": [serialize_user(u) for u in result["items"]],
        "pagination": result["pagination"],
    }), 200


@users_bp.route("", methods=["POST"])
@jwt_required()
@tenant_required
@admin_required
def create_user():
    """
    Create a new user in the current tenant (Admin only).
    ---
    tags:
      - Users
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [name, email, password]
          properties:
            name:
              type: string
            email:
              type: string
            password:
              type: string
            role:
              type: string
              enum: [admin, manager, user]
    responses:
      201:
        description: User created
      409:
        description: Email already exists in tenant
    """
    data, errors = validate_create_user(request.get_json() or {})
    if errors:
        return handle_validation_error(errors)

    tenant_id = get_current_tenant_id()

    if User.query.filter_by(email=data["email"], tenant_id=tenant_id).first():
        return jsonify({"error": "Email already exists in this tenant"}), 409

    user = User(
        tenant_id=tenant_id,
        name=data["name"],
        email=data["email"],
        role=data.get("role", "user"),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created", "user": serialize_user(user)}), 201
