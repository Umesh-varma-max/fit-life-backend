# routes/recommendation_routes.py
from flask import Blueprint, request
from middleware.auth_middleware import jwt_required_custom
from controllers.recommendation_controller import get_recommendation, generate_recommendation_payload

recommend_bp = Blueprint('recommendations', __name__, url_prefix='/api')


@recommend_bp.route('/recommendations', methods=['GET'])
@jwt_required_custom
def recommendations(current_user):
    return get_recommendation(current_user.id, request.args.get('goal'))


@recommend_bp.route('/recommendations/generate', methods=['POST'])
@jwt_required_custom
def recommendations_generate(current_user):
    data = request.get_json(silent=True) or {}
    return generate_recommendation_payload(
        current_user.id,
        goal=data.get('goal'),
        prompt_text=data.get('prompt_text')
    )
