from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from datetime import datetime

from app.extensions import db
from app.models.incident import Incident
from app.models.user import User
from app.schemas.validators import (
    validate_create_incident,
    validate_update_incident,
    validate_assign_incident,
)
from app.schemas.serializers import serialize_incident
from app.middleware.auth_middleware import (
    tenant_required, manager_or_admin_required,
    get_current_tenant_id, get_current_user_id, get_current_user_role,
)
from app.services.activity_service import log_activity
from app.utils.errors import handle_validation_error, handle_not_found, handle_conflict
from app.utils.pagination import paginate_query

incidents_bp = Blueprint("incidents", __name__, url_prefix="/api/incidents")


def _get_incident(incident_id, tenant_id):
    """Fetch an incident scoped to tenant, or return None."""
    return Incident.query.filter_by(id=incident_id, tenant_id=tenant_id).first()


@incidents_bp.route("", methods=["GET"])
@jwt_required()
@tenant_required
def list_incidents():
    """
    List incidents for the current tenant with filtering and pagination.
    ---
    tags:
      - Incidents
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
      - in: query
        name: priority
        type: string
      - in: query
        name: assigned_to
        type: integer
      - in: query
        name: search
        type: string
      - in: query
        name: page
        type: integer
      - in: query
        name: per_page
        type: integer
    responses:
      200:
        description: Paginated list of incidents
    """
    tenant_id = get_current_tenant_id()
    user_id = get_current_user_id()
    role = get_current_user_role()

    query = Incident.query.filter_by(tenant_id=tenant_id)

    # Regular users only see their assigned incidents
    if role == "user":
        query = query.filter_by(assigned_to=user_id)

    status = request.args.get("status")
    priority = request.args.get("priority")
    assigned_to = request.args.get("assigned_to", type=int)
    search = request.args.get("search", "").strip()

    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    if search:
        query = query.filter(Incident.title.ilike(f"%{search}%"))

    query = query.order_by(Incident.created_at.desc())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    result = paginate_query(query, page, per_page)

    return jsonify({
        "incidents": [serialize_incident(i) for i in result["items"]],
        "pagination": result["pagination"],
    }), 200


@incidents_bp.route("", methods=["POST"])
@jwt_required()
@tenant_required
@manager_or_admin_required
def create_incident():
    """
    Create a new incident.
    ---
    tags:
      - Incidents
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [title]
          properties:
            title:
              type: string
            description:
              type: string
            priority:
              type: string
              enum: [low, medium, high, critical]
            assigned_to:
              type: integer
    responses:
      201:
        description: Incident created
    """
    data, errors = validate_create_incident(request.get_json() or {})
    if errors:
        return handle_validation_error(errors)

    tenant_id = get_current_tenant_id()
    user_id = get_current_user_id()

    # Validate assigned_to belongs to same tenant
    if data.get("assigned_to"):
        if not User.query.filter_by(id=data["assigned_to"], tenant_id=tenant_id).first():
            return jsonify({"error": "Assigned user not found in this tenant"}), 404

    incident = Incident(
        tenant_id=tenant_id,
        title=data["title"],
        description=data.get("description"),
        priority=data.get("priority", "medium"),
        assigned_to=data.get("assigned_to"),
        created_by=user_id,
        status="open",
        version=1,
    )
    db.session.add(incident)
    db.session.flush()

    log_activity(
        tenant_id=tenant_id,
        incident_id=incident.id,
        action="created",
        created_by=user_id,
        new_value=incident.title,
    )
    db.session.commit()

    return jsonify({
        "message": "Incident created",
        "incident": serialize_incident(incident),
    }), 201


@incidents_bp.route("/<int:incident_id>", methods=["GET"])
@jwt_required()
@tenant_required
def get_incident(incident_id):
    """
    Get incident detail by ID.
    ---
    tags:
      - Incidents
    security:
      - Bearer: []
    parameters:
      - in: path
        name: incident_id
        type: integer
        required: true
    responses:
      200:
        description: Incident detail
      404:
        description: Not found
    """
    tenant_id = get_current_tenant_id()
    incident = _get_incident(incident_id, tenant_id)
    if not incident:
        return handle_not_found("Incident")

    return jsonify({"incident": serialize_incident(incident)}), 200


@incidents_bp.route("/<int:incident_id>", methods=["PUT"])
@jwt_required()
@tenant_required
@manager_or_admin_required
def update_incident(incident_id):
    """
    Update an incident (optimistic locking enforced via version field).
    ---
    tags:
      - Incidents
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
          required: [version]
          properties:
            title:
              type: string
            description:
              type: string
            status:
              type: string
            priority:
              type: string
            assigned_to:
              type: integer
            version:
              type: integer
    responses:
      200:
        description: Updated
      409:
        description: Version conflict (stale update)
    """
    data, errors = validate_update_incident(request.get_json() or {})
    if errors:
        return handle_validation_error(errors)

    tenant_id = get_current_tenant_id()
    user_id = get_current_user_id()
    incident = _get_incident(incident_id, tenant_id)
    if not incident:
        return handle_not_found("Incident")

    # Optimistic concurrency check
    if incident.version != data["version"]:
        return handle_conflict(
            f"Stale data: expected version {incident.version}, got {data['version']}"
        )

    updatable = ["title", "description", "status", "priority", "assigned_to"]
    changes = []
    for field in updatable:
        if field in data and getattr(incident, field) != data[field]:
            old_val = getattr(incident, field)
            setattr(incident, field, data[field])
            changes.append((field, old_val, data[field]))

    if changes:
        incident.version += 1
        incident.updated_at = datetime.utcnow()
        for field, old_val, new_val in changes:
            log_activity(
                tenant_id=tenant_id,
                incident_id=incident.id,
                action=f"{field}_changed",
                created_by=user_id,
                old_value=old_val,
                new_value=new_val,
            )
        db.session.commit()

    return jsonify({
        "message": "Incident updated",
        "incident": serialize_incident(incident),
    }), 200


@incidents_bp.route("/<int:incident_id>/resolve", methods=["PATCH"])
@jwt_required()
@tenant_required
@manager_or_admin_required
def resolve_incident(incident_id):
    """
    Resolve an incident.
    ---
    tags:
      - Incidents
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
          required: [version]
          properties:
            version:
              type: integer
    responses:
      200:
        description: Resolved
      409:
        description: Version conflict
    """
    body = request.get_json() or {}
    version = body.get("version")
    if version is None:
        return handle_validation_error({"version": ["version is required"]})

    try:
        version = int(version)
    except (TypeError, ValueError):
        return handle_validation_error({"version": ["version must be an integer"]})

    tenant_id = get_current_tenant_id()
    user_id = get_current_user_id()
    incident = _get_incident(incident_id, tenant_id)
    if not incident:
        return handle_not_found("Incident")

    if incident.version != version:
        return handle_conflict(
            f"Stale data: expected version {incident.version}, got {version}"
        )

    old_status = incident.status
    incident.status = "resolved"
    incident.version += 1
    incident.updated_at = datetime.utcnow()

    log_activity(
        tenant_id=tenant_id,
        incident_id=incident.id,
        action="status_changed",
        created_by=user_id,
        old_value=old_status,
        new_value="resolved",
    )
    db.session.commit()

    return jsonify({
        "message": "Incident resolved",
        "incident": serialize_incident(incident),
    }), 200


@incidents_bp.route("/<int:incident_id>/assign", methods=["PATCH"])
@jwt_required()
@tenant_required
@manager_or_admin_required
def assign_incident(incident_id):
    """
    Assign an incident to a user.
    ---
    tags:
      - Incidents
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
          required: [assigned_to, version]
          properties:
            assigned_to:
              type: integer
            version:
              type: integer
    responses:
      200:
        description: Assigned
      404:
        description: Incident or user not found
      409:
        description: Version conflict
    """
    data, errors = validate_assign_incident(request.get_json() or {})
    if errors:
        return handle_validation_error(errors)

    tenant_id = get_current_tenant_id()
    user_id = get_current_user_id()
    incident = _get_incident(incident_id, tenant_id)
    if not incident:
        return handle_not_found("Incident")

    if incident.version != data["version"]:
        return handle_conflict(
            f"Stale data: expected version {incident.version}, got {data['version']}"
        )

    # Validate assignee belongs to same tenant
    assignee = User.query.filter_by(id=data["assigned_to"], tenant_id=tenant_id).first()
    if not assignee:
        return handle_not_found("Assignee user")

    old_assigned = incident.assigned_to
    incident.assigned_to = data["assigned_to"]
    incident.status = "in_progress" if incident.status == "open" else incident.status
    incident.version += 1
    incident.updated_at = datetime.utcnow()

    log_activity(
        tenant_id=tenant_id,
        incident_id=incident.id,
        action="assigned",
        created_by=user_id,
        old_value=old_assigned,
        new_value=data["assigned_to"],
    )
    db.session.commit()

    return jsonify({
        "message": "Incident assigned",
        "incident": serialize_incident(incident),
    }), 200
