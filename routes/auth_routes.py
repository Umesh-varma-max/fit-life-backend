# routes/auth_routes.py
from flask import Blueprint, jsonify
from extensions import limiter
from middleware.validation_middleware import validate_body
from schemas.auth_schema import RegisterSchema, LoginSchema
from controllers.auth_controller import register_user, login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("30 per hour;10 per minute")
@validate_body(RegisterSchema)
def register(validated_data):
    return register_user(validated_data)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("60 per hour;20 per minute")
@validate_body(LoginSchema)
def login(validated_data):
    return login_user(validated_data)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    # JWT is stateless — client just deletes the token
    return jsonify({"status": "success", "message": "Logged out"}), 200
