# routes/reminder_routes.py
from flask import Blueprint
from middleware.auth_middleware import jwt_required_custom
from middleware.validation_middleware import validate_body
from schemas.reminder_schema import ReminderSchema
from controllers.reminder_controller import list_reminders, add_reminder, delete_reminder

reminder_bp = Blueprint('reminders', __name__, url_prefix='/api')


@reminder_bp.route('/reminders', methods=['GET'])
@jwt_required_custom
def reminders_list(current_user):
    return list_reminders(current_user.id)


@reminder_bp.route('/reminders', methods=['POST'])
@jwt_required_custom
@validate_body(ReminderSchema)
def reminders_add(current_user, validated_data):
    return add_reminder(current_user.id, validated_data)


@reminder_bp.route('/reminders/<int:reminder_id>', methods=['DELETE'])
@jwt_required_custom
def reminders_delete(current_user, reminder_id):
    return delete_reminder(current_user.id, reminder_id)
