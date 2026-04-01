# routes/workout_routes.py
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import jwt_required_custom
from middleware.validation_middleware import validate_body
from schemas.workout_schema import WorkoutPlanSchema
from controllers.workout_controller import (
    get_plan,
    save_plan,
    log_timer,
    generate_workout_plan,
    log_completed_workout,
)

workout_bp = Blueprint('workout', __name__, url_prefix='/api/workout')


@workout_bp.route('/plan', methods=['GET'])
@jwt_required_custom
def workout_get(current_user):
    return get_plan(current_user.id, request.args.get('goal'))


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


@workout_bp.route('/generate', methods=['POST'])
@jwt_required_custom
def workout_generate(current_user):
    data = request.get_json(silent=True) or {}
    return generate_workout_plan(
        current_user.id,
        goal=data.get('goal'),
        prompt_text=data.get('prompt_text')
    )


@workout_bp.route('/complete', methods=['POST'])
@jwt_required_custom
def workout_complete(current_user):
    data = request.get_json(silent=True) or {}
    exercises = data.get('exercises') or []
    if not exercises:
        return jsonify({"status": "error", "message": "exercises are required"}), 400
    return log_completed_workout(current_user.id, data)
