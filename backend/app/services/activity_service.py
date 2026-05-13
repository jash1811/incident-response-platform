from app.models.activity_log import ActivityLog
from app.extensions import db
from datetime import datetime


def log_activity(tenant_id: int, incident_id: int, action: str,
                 created_by: int, old_value=None, new_value=None):
    """
    Create an activity log entry for an incident action.
    Always call within an existing DB transaction.
    """
    log = ActivityLog(
        tenant_id=tenant_id,
        incident_id=incident_id,
        action=action,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )
    db.session.add(log)
    # Caller is responsible for db.session.commit()
    return log
