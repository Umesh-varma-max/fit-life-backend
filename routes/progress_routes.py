# routes/progress_routes.py
from flask import Blueprint, request
from middleware.auth_middleware import jwt_required_custom
from controllers.progress_controller import get_progress

progress_bp = Blueprint('progress', __name__, url_prefix='/api')


@progress_bp.route('/progress', methods=['GET'])
@jwt_required_custom
def progress(current_user):
    period = request.args.get('period', 'weekly')
    if period not in ('weekly', 'monthly'):
        period = 'weekly'
    return get_progress(current_user.id, period)
