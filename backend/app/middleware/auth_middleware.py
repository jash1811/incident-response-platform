from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def tenant_required(fn):
    """Ensure JWT has a valid tenant_id claim."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if "tenant_id" not in claims:
            return jsonify({"error": "Missing tenant context in token"}), 403
        return fn(*args, **kwargs)
    return wrapper


def role_required(*roles):
    """Restrict endpoint to users with specific roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "")
            if user_role not in roles:
                return jsonify(
                    {"error": f"Access denied. Required roles: {list(roles)}"}
                ), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    return role_required("admin")(fn)


def manager_or_admin_required(fn):
    return role_required("admin", "manager")(fn)


def get_current_tenant_id():
    """Extract tenant_id from JWT claims."""
    claims = get_jwt()
    return claims.get("tenant_id")


def get_current_user_id():
    """Extract user id from JWT claims."""
    claims = get_jwt()
    return claims.get("user_id")


def get_current_user_role():
    """Extract user role from JWT claims."""
    claims = get_jwt()
    return claims.get("role")
