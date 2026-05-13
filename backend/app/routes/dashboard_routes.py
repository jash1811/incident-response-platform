from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.incident import Incident
from app.models.user import User
from app.middleware.auth_middleware import tenant_required, get_current_tenant_id

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/stats", methods=["GET"])
@jwt_required()
@tenant_required
def get_stats():
    """
    Get dashboard statistics for the current tenant.
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard stats
    """
    tenant_id = get_current_tenant_id()

    total = Incident.query.filter_by(tenant_id=tenant_id).count()
    open_count = Incident.query.filter_by(tenant_id=tenant_id, status="open").count()
    in_progress = Incident.query.filter_by(tenant_id=tenant_id, status="in_progress").count()
    resolved = Incident.query.filter_by(tenant_id=tenant_id, status="resolved").count()
    closed = Incident.query.filter_by(tenant_id=tenant_id, status="closed").count()
    total_users = User.query.filter_by(tenant_id=tenant_id).count()

    # Priority breakdown
    priority_breakdown = (
        db.session.query(Incident.priority, func.count(Incident.id))
        .filter_by(tenant_id=tenant_id)
        .group_by(Incident.priority)
        .all()
    )

    # Recent incidents
    recent = (
        Incident.query.filter_by(tenant_id=tenant_id)
        .order_by(Incident.created_at.desc())
        .limit(5)
        .all()
    )

    from app.schemas.serializers import serialize_incident

    return jsonify({
        "stats": {
            "total_incidents": total,
            "open": open_count,
            "in_progress": in_progress,
            "resolved": resolved,
            "closed": closed,
            "total_users": total_users,
            "priority_breakdown": {row[0]: row[1] for row in priority_breakdown},
        },
        "recent_incidents": [serialize_incident(i) for i in recent],
    }), 200
