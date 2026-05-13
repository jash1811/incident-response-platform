from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.validators import validate_register, validate_login
from app.schemas.serializers import serialize_user
from app.utils.errors import handle_validation_error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new tenant and admin user.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [name, email, password, tenant_name]
          properties:
            name:
              type: string
            email:
              type: string
            password:
              type: string
            tenant_name:
              type: string
            role:
              type: string
              enum: [admin, manager, user]
    responses:
      201:
        description: Registration successful
      422:
        description: Validation error
      409:
        description: Email already exists in tenant
    """
    data, errors = validate_register(request.get_json() or {})
    if errors:
        return handle_validation_error(errors)

    # Reuse existing tenant or create a new one
    tenant = Tenant.query.filter_by(name=data["tenant_name"]).first()
    if not tenant:
        tenant = Tenant(name=data["tenant_name"])
        db.session.add(tenant)
        db.session.flush()  # get tenant.id before user insert

    # Prevent duplicate email within the same tenant
    if User.query.filter_by(email=data["email"], tenant_id=tenant.id).first():
        return jsonify({"error": "Email already registered in this tenant"}), 409

    user = User(
        tenant_id=tenant.id,
        name=data["name"],
        email=data["email"],
        role=data.get("role", "admin"),
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "tenant_id": tenant.id,
            "role": user.role,
            "user_id": user.id,
        },
    )

    return jsonify({
        "message": "Registration successful",
        "access_token": token,
        "user": serialize_user(user),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate user and return JWT token.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data, errors = validate_login(request.get_json() or {})
    if errors:
        return handle_validation_error(errors)

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "tenant_id": user.tenant_id,
            "role": user.role,
            "user_id": user.id,
        },
    )

    return jsonify({
        "access_token": token,
        "user": serialize_user(user),
    }), 200
