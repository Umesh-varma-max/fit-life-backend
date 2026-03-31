# routes/doctor_routes.py
from flask import Blueprint, request
from middleware.auth_middleware import jwt_required_custom
from controllers.doctor_controller import list_doctors

doctor_bp = Blueprint('doctors', __name__, url_prefix='/api')


@doctor_bp.route('/doctors', methods=['GET'])
@jwt_required_custom
def doctors(current_user):
    specialization = request.args.get('specialization', '')
    return list_doctors(specialization)
