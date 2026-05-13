from app.extensions import db
from datetime import datetime


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    __table_args__ = (
        db.Index("ix_activity_incident_id", "incident_id"),
        db.Index("ix_activity_tenant_id", "tenant_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    incident_id = db.Column(
        db.Integer, db.ForeignKey("incidents.id"), nullable=False
    )
    action = db.Column(db.String(100), nullable=False)  # e.g. "status_changed", "assigned"
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ActivityLog {self.action} on Incident {self.incident_id}>"
