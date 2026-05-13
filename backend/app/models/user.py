import bcrypt
from app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.Index("ix_users_tenant_id", "tenant_id"),
        db.Index("ix_users_email_tenant", "email", "tenant_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum("admin", "manager", "user"), nullable=False, default="user"
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    assigned_incidents = db.relationship(
        "Incident",
        foreign_keys="Incident.assigned_to",
        backref="assignee",
        lazy="dynamic",
    )
    created_incidents = db.relationship(
        "Incident",
        foreign_keys="Incident.created_by",
        backref="creator",
        lazy="dynamic",
    )
    comments = db.relationship("IncidentComment", backref="author", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def __repr__(self):
        return f"<User {self.email}>"
