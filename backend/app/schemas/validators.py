"""
Manual input validation — no marshmallow dependency.
Each validate_* function returns (data_dict, errors_dict).
errors_dict is empty on success.
"""
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

VALID_ROLES = {"admin", "manager", "user"}
VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}


def _err(field, msg):
    return {field: [msg]}


def validate_register(raw: dict):
    errors = {}
    data = {}

    name = str(raw.get("name", "") or "").strip()
    if not name:
        errors["name"] = ["Name is required"]
    elif len(name) < 2 or len(name) > 255:
        errors["name"] = ["Name must be 2–255 characters"]
    else:
        data["name"] = name

    email = str(raw.get("email", "") or "").strip().lower()
    if not email:
        errors["email"] = ["Email is required"]
    elif not EMAIL_RE.match(email):
        errors["email"] = ["Invalid email address"]
    else:
        data["email"] = email

    password = str(raw.get("password", "") or "")
    if not password:
        errors["password"] = ["Password is required"]
    elif len(password) < 6:
        errors["password"] = ["Password must be at least 6 characters"]
    else:
        data["password"] = password

    tenant_name = str(raw.get("tenant_name", "") or "").strip()
    if not tenant_name:
        errors["tenant_name"] = ["Organization name is required"]
    elif len(tenant_name) < 2 or len(tenant_name) > 255:
        errors["tenant_name"] = ["Organization name must be 2–255 characters"]
    else:
        data["tenant_name"] = tenant_name

    role = str(raw.get("role", "admin") or "admin").strip()
    if role not in VALID_ROLES:
        errors["role"] = [f"Role must be one of: {', '.join(VALID_ROLES)}"]
    else:
        data["role"] = role

    return data, errors


def validate_login(raw: dict):
    errors = {}
    data = {}

    email = str(raw.get("email", "") or "").strip().lower()
    if not email:
        errors["email"] = ["Email is required"]
    elif not EMAIL_RE.match(email):
        errors["email"] = ["Invalid email address"]
    else:
        data["email"] = email

    password = str(raw.get("password", "") or "")
    if not password:
        errors["password"] = ["Password is required"]
    else:
        data["password"] = password

    return data, errors


def validate_create_user(raw: dict):
    errors = {}
    data = {}

    name = str(raw.get("name", "") or "").strip()
    if not name:
        errors["name"] = ["Name is required"]
    elif len(name) < 2 or len(name) > 255:
        errors["name"] = ["Name must be 2–255 characters"]
    else:
        data["name"] = name

    email = str(raw.get("email", "") or "").strip().lower()
    if not email:
        errors["email"] = ["Email is required"]
    elif not EMAIL_RE.match(email):
        errors["email"] = ["Invalid email address"]
    else:
        data["email"] = email

    password = str(raw.get("password", "") or "")
    if not password:
        errors["password"] = ["Password is required"]
    elif len(password) < 6:
        errors["password"] = ["Password must be at least 6 characters"]
    else:
        data["password"] = password

    role = str(raw.get("role", "user") or "user").strip()
    if role not in VALID_ROLES:
        errors["role"] = [f"Role must be one of: {', '.join(VALID_ROLES)}"]
    else:
        data["role"] = role

    return data, errors


def validate_create_incident(raw: dict):
    errors = {}
    data = {}

    title = str(raw.get("title", "") or "").strip()
    if not title:
        errors["title"] = ["Title is required"]
    elif len(title) < 3 or len(title) > 500:
        errors["title"] = ["Title must be 3–500 characters"]
    else:
        data["title"] = title

    description = raw.get("description")
    data["description"] = str(description).strip() if description else None

    priority = str(raw.get("priority", "medium") or "medium").strip()
    if priority not in VALID_PRIORITIES:
        errors["priority"] = [f"Priority must be one of: {', '.join(VALID_PRIORITIES)}"]
    else:
        data["priority"] = priority

    assigned_to = raw.get("assigned_to")
    if assigned_to is not None:
        try:
            data["assigned_to"] = int(assigned_to)
        except (TypeError, ValueError):
            errors["assigned_to"] = ["assigned_to must be an integer"]
    else:
        data["assigned_to"] = None

    return data, errors


def validate_update_incident(raw: dict):
    errors = {}
    data = {}

    # version is required for optimistic locking
    version = raw.get("version")
    if version is None:
        errors["version"] = ["version is required"]
    else:
        try:
            data["version"] = int(version)
        except (TypeError, ValueError):
            errors["version"] = ["version must be an integer"]

    if "title" in raw:
        title = str(raw["title"] or "").strip()
        if len(title) < 3 or len(title) > 500:
            errors["title"] = ["Title must be 3–500 characters"]
        else:
            data["title"] = title

    if "description" in raw:
        data["description"] = str(raw["description"]).strip() if raw["description"] else None

    if "status" in raw:
        status = str(raw["status"] or "").strip()
        if status not in VALID_STATUSES:
            errors["status"] = [f"Status must be one of: {', '.join(VALID_STATUSES)}"]
        else:
            data["status"] = status

    if "priority" in raw:
        priority = str(raw["priority"] or "").strip()
        if priority not in VALID_PRIORITIES:
            errors["priority"] = [f"Priority must be one of: {', '.join(VALID_PRIORITIES)}"]
        else:
            data["priority"] = priority

    if "assigned_to" in raw:
        assigned_to = raw["assigned_to"]
        if assigned_to is None:
            data["assigned_to"] = None
        else:
            try:
                data["assigned_to"] = int(assigned_to)
            except (TypeError, ValueError):
                errors["assigned_to"] = ["assigned_to must be an integer"]

    return data, errors


def validate_assign_incident(raw: dict):
    errors = {}
    data = {}

    assigned_to = raw.get("assigned_to")
    if assigned_to is None:
        errors["assigned_to"] = ["assigned_to is required"]
    else:
        try:
            data["assigned_to"] = int(assigned_to)
        except (TypeError, ValueError):
            errors["assigned_to"] = ["assigned_to must be an integer"]

    version = raw.get("version")
    if version is None:
        errors["version"] = ["version is required"]
    else:
        try:
            data["version"] = int(version)
        except (TypeError, ValueError):
            errors["version"] = ["version must be an integer"]

    return data, errors


def validate_add_comment(raw: dict):
    errors = {}
    data = {}

    comment = str(raw.get("comment", "") or "").strip()
    if not comment:
        errors["comment"] = ["Comment is required"]
    elif len(comment) > 5000:
        errors["comment"] = ["Comment must be 5000 characters or fewer"]
    else:
        data["comment"] = comment

    return data, errors
