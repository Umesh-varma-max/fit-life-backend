# routes/recommendation_routes.py
from flask import Blueprint
from middleware.auth_middleware import jwt_required_custom
from controllers.recommendation_controller import get_recommendation

recommend_bp = Blueprint('recommendations', __name__, url_prefix='/api')


@recommend_bp.route('/recommendations', methods=['GET'])
@jwt_required_custom
def recommendations(current_user):
    return get_recommendation(current_user.id)
