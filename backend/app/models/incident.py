from app.extensions import db
from datetime import datetime


class Incident(db.Model):
    __tablename__ = "incidents"
    __table_args__ = (
        db.Index("ix_incidents_tenant_id", "tenant_id"),
        db.Index("ix_incidents_status", "status"),
        db.Index("ix_incidents_assigned_to", "assigned_to"),
        db.Index("ix_incidents_tenant_status", "tenant_id", "status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum("open", "in_progress", "resolved", "closed"),
        nullable=False,
        default="open",
    )
    priority = db.Column(
        db.Enum("low", "medium", "high", "critical"),
        nullable=False,
        default="medium",
    )
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Optimistic concurrency control
    version = db.Column(db.Integer, nullable=False, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    comments = db.relationship(
        "IncidentComment", backref="incident", lazy="dynamic", cascade="all, delete-orphan"
    )
    activity_logs = db.relationship(
        "ActivityLog", backref="incident", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Incident {self.id}: {self.title[:30]}>"
