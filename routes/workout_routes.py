# routes/workout_routes.py
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import jwt_required_custom
from middleware.validation_middleware import validate_body
from schemas.workout_schema import WorkoutPlanSchema
from controllers.workout_controller import get_plan, save_plan, log_timer

workout_bp = Blueprint('workout', __name__, url_prefix='/api/workout')


@workout_bp.route('/plan', methods=['GET'])
@jwt_required_custom
def workout_get(current_user):
    return get_plan(current_user.id)


@workout_bp.route('/plan', methods=['POST'])
@jwt_required_custom
@validate_body(WorkoutPlanSchema)
def workout_save(current_user, validated_data):
    return save_plan(current_user.id, validated_data)


@workout_bp.route('/timer', methods=['POST'])
@jwt_required_custom
def workout_timer(current_user):
    data = request.get_json(silent=True) or {}
    if not data.get('exercise_name'):
        return jsonify({"status": "error", "message": "exercise_name is required"}), 400
    if not data.get('duration_seconds'):
        return jsonify({"status": "error", "message": "duration_seconds is required"}), 400
    return log_timer(current_user.id, data)
