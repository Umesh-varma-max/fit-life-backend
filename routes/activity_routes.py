# routes/activity_routes.py
from flask import Blueprint, request
from middleware.auth_middleware import jwt_required_custom
from middleware.validation_middleware import validate_body
from schemas.activity_schema import ActivityLogSchema
from controllers.activity_controller import log_activity, get_activity
from datetime import date

activity_bp = Blueprint('activity', __name__, url_prefix='/api')


@activity_bp.route('/activity', methods=['POST'])
@jwt_required_custom
@validate_body(ActivityLogSchema)
def activity_log(current_user, validated_data):
    return log_activity(current_user.id, validated_data)


@activity_bp.route('/activity', methods=['GET'])
@jwt_required_custom
def activity_get(current_user):
    date_str = request.args.get('date')
    log_date = None
    if date_str:
        try:
            log_date = date.fromisoformat(date_str)
        except ValueError:
            log_date = date.today()
    return get_activity(current_user.id, log_date)
