# routes/export_routes.py
from flask import Blueprint
from extensions import limiter
from middleware.auth_middleware import jwt_required_custom
from controllers.export_controller import export_pdf

export_bp = Blueprint('export', __name__, url_prefix='/api')


@export_bp.route('/export/pdf', methods=['GET'])
@jwt_required_custom
@limiter.limit("5 per hour")
def pdf_export(current_user):
    return export_pdf(current_user)
