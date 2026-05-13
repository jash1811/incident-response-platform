"""
Plain serializers — convert SQLAlchemy model instances to dicts.
No third-party dependency required.
"""


def _fmt_dt(dt):
    """Format a datetime to ISO string, or None."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S") if dt else None


def serialize_user(user):
    return {
        "id": user.id,
        "tenant_id": user.tenant_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": _fmt_dt(user.created_at),
    }


def serialize_incident(incident):
    return {
        "id": incident.id,
        "tenant_id": incident.tenant_id,
        "title": incident.title,
        "description": incident.description,
        "status": incident.status,
        "priority": incident.priority,
        "assigned_to": incident.assigned_to,
        "assignee_name": incident.assignee.name if incident.assignee else None,
        "created_by": incident.created_by,
        "creator_name": incident.creator.name if incident.creator else None,
        "version": incident.version,
        "created_at": _fmt_dt(incident.created_at),
        "updated_at": _fmt_dt(incident.updated_at),
    }


def serialize_comment(comment):
    return {
        "id": comment.id,
        "tenant_id": comment.tenant_id,
        "incident_id": comment.incident_id,
        "user_id": comment.user_id,
        "author_name": comment.author.name if comment.author else None,
        "comment": comment.comment,
        "created_at": _fmt_dt(comment.created_at),
    }


def serialize_activity(log):
    from app.models.user import User
    actor = User.query.get(log.created_by)
    return {
        "id": log.id,
        "tenant_id": log.tenant_id,
        "incident_id": log.incident_id,
        "action": log.action,
        "old_value": log.old_value,
        "new_value": log.new_value,
        "created_by": log.created_by,
        "actor_name": actor.name if actor else "Unknown",
        "created_at": _fmt_dt(log.created_at),
    }
