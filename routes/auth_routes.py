# routes/auth_routes.py
from flask import Blueprint
from flask_jwt_extended import jwt_required
from extensions import limiter
from middleware.auth_middleware import jwt_required_custom
from middleware.validation_middleware import validate_body
from schemas.auth_schema import RegisterSchema, LoginSchema
from controllers.auth_controller import (
    get_current_user,
    login_user,
    logout_user,
    refresh_session,
    register_user
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api')


@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per hour")
@validate_body(RegisterSchema)
def register(validated_data):
    return register_user(validated_data)


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("20 per hour")
@validate_body(LoginSchema)
def login(validated_data):
    return login_user(validated_data)


@auth_bp.route('/logout', methods=['POST'])
@jwt_required_custom
def logout(current_user):
    return logout_user()


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    return refresh_session()


@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def me(current_user):
    return get_current_user(current_user)
