# middleware/auth_middleware.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User


def jwt_required_custom(f):
    """
    Custom JWT middleware decorator.
    Verifies token, loads user from DB, passes current_user to controller.

    Usage:
        @jwt_required_custom
        def my_route(current_user):
            ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 401
        except Exception:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401
        return f(*args, current_user=user, **kwargs)
    return decorated
