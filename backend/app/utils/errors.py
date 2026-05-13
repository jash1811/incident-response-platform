from flask import jsonify


def handle_validation_error(messages: dict):
    """Return a 422 response with field-level error messages."""
    return jsonify({"error": "Validation failed", "messages": messages}), 422


def handle_not_found(resource="Resource"):
    return jsonify({"error": f"{resource} not found"}), 404


def handle_conflict(message="Conflict"):
    return jsonify({"error": message}), 409


def handle_forbidden(message="Forbidden"):
    return jsonify({"error": message}), 403


def handle_server_error(e: Exception = None):
    # TODO: integrate with error tracking (e.g., Sentry) in production
    msg = str(e) if e else "Internal server error"
    return jsonify({"error": msg}), 500
