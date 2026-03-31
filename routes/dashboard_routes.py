# routes/dashboard_routes.py
from flask import Blueprint
from middleware.auth_middleware import jwt_required_custom
from controllers.dashboard_controller import get_dashboard

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')


@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required_custom
def dashboard(current_user):
    return get_dashboard(current_user.id)
