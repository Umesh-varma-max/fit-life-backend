# routes/trainer_routes.py
from flask import Blueprint, request
from middleware.auth_middleware import jwt_required_custom
from controllers.trainer_controller import list_trainers

trainer_bp = Blueprint('trainers', __name__, url_prefix='/api')


@trainer_bp.route('/trainers', methods=['GET'])
@jwt_required_custom
def trainers(current_user):
    location = request.args.get('location', '')
    return list_trainers(location)
