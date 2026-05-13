from app.extensions import db
from datetime import datetime


class IncidentComment(db.Model):
    __tablename__ = "incident_comments"
    __table_args__ = (
        db.Index("ix_comments_incident_id", "incident_id"),
        db.Index("ix_comments_tenant_id", "tenant_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    incident_id = db.Column(
        db.Integer, db.ForeignKey("incidents.id"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Comment {self.id} on Incident {self.incident_id}>"
