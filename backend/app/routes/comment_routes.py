from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.comment import IncidentComment
from app.models.activity_log import ActivityLog
from app.models.incident import Incident
from app.schemas.validators import validate_add_comment
from app.schemas.serializers import serialize_comment, serialize_activity
from app.middleware.auth_middleware import (
    tenant_required, get_current_tenant_id, get_current_user_id,
)
from app.utils.errors import handle_validation_error, handle_not_found
from app.utils.pagination import paginate_query

comments_bp = Blueprint("comments", __name__, url_prefix="/api/incidents")


@comments_bp.route("/<int:incident_id>/comments", methods=["POST"])
@jwt_required()
@tenant_required
def add_comment(incident_id):
    """
    Add a comment to an incident.
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [comment]
          properties:
            comment:
              type: string
    responses:
      201:
        description: Comment added
      404:
        description: Incident not found
    """
    data, errors = validate_add_comment(request.get_json() or {})
    if errors:
        return handle_validation_error(errors)

    tenant_id = get_current_tenant_id()
    user_id = get_current_user_id()

    incident = Incident.query.filter_by(id=incident_id, tenant_id=tenant_id).first()
    if not incident:
        return handle_not_found("Incident")

    comment = IncidentComment(
        tenant_id=tenant_id,
        incident_id=incident_id,
        user_id=user_id,
        comment=data["comment"],
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        "message": "Comment added",
        "comment": serialize_comment(comment),
    }), 201


@comments_bp.route("/<int:incident_id>/comments", methods=["GET"])
@jwt_required()
@tenant_required
def get_comments(incident_id):
    """
    Get all comments for an incident.
    ---
    tags:
      - Comments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
    responses:
      200:
        description: List of comments
      404:
        description: Incident not found
    """
    tenant_id = get_current_tenant_id()

    incident = Incident.query.filter_by(id=incident_id, tenant_id=tenant_id).first()
    if not incident:
        return handle_not_found("Incident")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    query = IncidentComment.query.filter_by(
        incident_id=incident_id, tenant_id=tenant_id
    ).order_by(IncidentComment.created_at.asc())

    result = paginate_query(query, page, per_page)

    return jsonify({
        "comments": [serialize_comment(c) for c in result["items"]],
        "pagination": result["pagination"],
    }), 200


@comments_bp.route("/<int:incident_id>/activity", methods=["GET"])
@jwt_required()
@tenant_required
def get_activity(incident_id):
    """
    Get activity timeline for an incident.
    ---
    tags:
      - Activity
    security:
      - Bearer: []
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
    responses:
      200:
        description: Activity log
      404:
        description: Incident not found
    """
    tenant_id = get_current_tenant_id()

    incident = Incident.query.filter_by(id=incident_id, tenant_id=tenant_id).first()
    if not incident:
        return handle_not_found("Incident")

    logs = ActivityLog.query.filter_by(
        incident_id=incident_id, tenant_id=tenant_id
    ).order_by(ActivityLog.created_at.asc()).all()

    return jsonify({"activity": [serialize_activity(log) for log in logs]}), 200
