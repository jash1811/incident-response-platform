from app.extensions import db
from datetime import datetime


class Tenant(db.Model):
    __tablename__ = "tenants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    users = db.relationship("User", backref="tenant", lazy="dynamic")
    incidents = db.relationship("Incident", backref="tenant", lazy="dynamic")

    def __repr__(self):
        return f"<Tenant {self.name}>"
