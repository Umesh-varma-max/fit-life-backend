# routes/profile_routes.py
from flask import Blueprint
from middleware.auth_middleware import jwt_required_custom
from middleware.validation_middleware import validate_body
from schemas.profile_schema import HealthProfileSchema
from controllers.profile_controller import get_profile, save_profile

profile_bp = Blueprint('profile', __name__, url_prefix='/api')


@profile_bp.route('/profile', methods=['GET'])
@jwt_required_custom
def profile_get(current_user):
    return get_profile(current_user.id)


@profile_bp.route('/profile', methods=['POST'])
@jwt_required_custom
@validate_body(HealthProfileSchema)
def profile_save(current_user, validated_data):
    return save_profile(current_user.id, validated_data)
