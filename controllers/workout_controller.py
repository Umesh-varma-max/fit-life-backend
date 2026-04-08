from datetime import date, datetime

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.workout_plan import WorkoutPlan
from models.workout_session import WorkoutSession
from utils.workout_library_engine import generate_personalized_workout_plan
from utils.workout_templates import DAY_ORDER, build_workout_day


def _serialize_custom_plans(plans) -> list:
    enriched_days = [
        build_workout_day(plan.day_of_week, plan.exercises or [], plan.plan_name)
        for plan in plans
    ]
    return sorted(enriched_days, key=lambda item: DAY_ORDER.index(item['day']))


def _plan_summary(enriched_plan: list) -> dict:
    return {
        'total_days': len(enriched_plan),
        'active_days': sum(1 for day in enriched_plan if day['total_duration_min'] > 0),
        'total_duration_min': sum(day['total_duration_min'] for day in enriched_plan),
        'total_estimated_calories_burn': sum(day['total_estimated_calories_burn'] for day in enriched_plan)
    }


def _session_to_response(session: WorkoutSession):
    payload = session.to_dict()
    plan_snapshot = payload.get('plan_snapshot') or []
    payload['current_exercise'] = (
        plan_snapshot[payload['current_exercise_index']]
        if payload['current_exercise_index'] < len(plan_snapshot)
        else None
    )
    return payload


def get_plan(user_id: int):
    """Return a profile-aware workout plan and include custom plans when they exist."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    generated_plan = generate_personalized_workout_plan(profile)

    custom_plans = WorkoutPlan.query.filter_by(user_id=user_id).all()
    custom_plans = sorted(
        custom_plans,
        key=lambda item: DAY_ORDER.index(item.day_of_week) if item.day_of_week in DAY_ORDER else 99
    )

    response_payload = {
        "status": "success",
        "source": "personalized",
        "goal": generated_plan['goal'],
        "goal_label": generated_plan['goal_label'],
        "goal_badge": generated_plan['goal_badge'],
        "hero_image_url": generated_plan['hero_image_url'],
        "recommended_plan_tier": generated_plan['recommended_plan_tier'],
        "goal_eta_weeks": generated_plan['goal_eta_weeks'],
        "bmi_category": generated_plan['bmi_category'],
        "body_fat_category": generated_plan['body_fat_category'],
        "template_key": generated_plan['template_key'],
        "total_days": generated_plan['total_days'],
        "active_days": generated_plan['active_days'],
        "total_duration_min": generated_plan['total_duration_min'],
        "total_estimated_calories_burn": generated_plan['total_estimated_calories_burn'],
        "today_day": generated_plan['today_day'],
        "today_plan": generated_plan['today_plan'],
        "workout_stats": {
            "exercise_count": (generated_plan['today_plan'] or {}).get('exercise_count', len((generated_plan['today_plan'] or {}).get('exercises', []))),
            "minutes": (generated_plan['today_plan'] or {}).get('total_duration_min', 0),
            "calories": (generated_plan['today_plan'] or {}).get('total_estimated_calories_burn', 0)
        },
        "plan": generated_plan['days'],
        "has_library_data": generated_plan['has_library_data']
    }

    if custom_plans:
        custom_serialized = _serialize_custom_plans(custom_plans)
        response_payload["custom_plan"] = {
            "source": "custom",
            **_plan_summary(custom_serialized),
            "days": custom_serialized
        }

    active_session = WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.created_at.desc()).first()
    if active_session:
        response_payload["active_session"] = _session_to_response(active_session)

    return jsonify(response_payload), 200


def save_plan(user_id: int, data: dict):
    """Create or update a workout plan for a specific day."""
    day = data['day']
    plan = WorkoutPlan.query.filter_by(user_id=user_id, day_of_week=day).first()

    if plan:
        plan.plan_name = data.get('plan_name') or plan.plan_name
        plan.exercises = data['exercises']
    else:
        plan = WorkoutPlan(
            user_id=user_id,
            day_of_week=day,
            plan_name=data.get('plan_name', f'{day} Workout'),
            exercises=data['exercises']
        )
        db.session.add(plan)

    db.session.commit()
    preview = build_workout_day(plan.day_of_week, plan.exercises or [], plan.plan_name)
    return jsonify({
        "status": "success",
        "message": "Workout plan saved",
        "plan_id": plan.id,
        "plan_preview": preview
    }), 200


def start_session(user_id: int, data: dict):
    """Start a workout session from the user's current personalized plan."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    generated_plan = generate_personalized_workout_plan(profile)
    requested_day = data.get('day') or generated_plan.get('today_day')
    selected_day = next((day for day in generated_plan.get('days', []) if day.get('day') == requested_day), None)

    if not selected_day:
        return jsonify({"status": "error", "message": "No workout day found to start"}), 404

    existing = WorkoutSession.query.filter_by(user_id=user_id, status='active').first()
    if existing:
        existing.status = 'reset'
        existing.completed_at = datetime.utcnow()

    session = WorkoutSession(
        user_id=user_id,
        goal=generated_plan.get('goal'),
        day_of_week=selected_day.get('day'),
        session_name=selected_day.get('session_title') or selected_day.get('plan_name'),
        status='active',
        current_exercise_index=0,
        plan_snapshot=selected_day.get('exercises', []),
        completed_exercises=[],
        total_duration_seconds=0,
        total_calories_burned=0
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Workout session started",
        "session": _session_to_response(session)
    }), 201


def get_active_session(user_id: int):
    session = WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.created_at.desc()).first()
    if not session:
        return jsonify({"status": "error", "message": "No active workout session"}), 404
    return jsonify({"status": "success", "session": _session_to_response(session)}), 200


def complete_session_exercise(user_id: int, session_id: int, data: dict):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"status": "error", "message": "Workout session not found"}), 404
    if session.status != 'active':
        return jsonify({"status": "error", "message": "Workout session is not active"}), 400

    current_index = session.current_exercise_index
    plan_snapshot = list(session.plan_snapshot or [])
    if current_index >= len(plan_snapshot):
        return jsonify({"status": "error", "message": "All exercises are already completed"}), 400

    exercise = dict(plan_snapshot[current_index])
    duration_seconds = int(data.get('duration_seconds') or exercise.get('duration_seconds') or 0)
    calories_burned = int(data.get('calories_burned') or exercise.get('estimated_calories_burn') or 0)
    completed_exercises = list(session.completed_exercises or [])
    completed_exercises.append({
        **exercise,
        'completed_at': datetime.utcnow().isoformat(),
        'duration_seconds': duration_seconds,
        'calories_burned': calories_burned
    })

    session.completed_exercises = completed_exercises
    session.total_duration_seconds = int(session.total_duration_seconds or 0) + duration_seconds
    session.total_calories_burned = int(session.total_calories_burned or 0) + calories_burned
    session.current_exercise_index = current_index + 1
    db.session.commit()

    is_complete = session.current_exercise_index >= len(plan_snapshot)
    return jsonify({
        "status": "success",
        "message": "Exercise completed",
        "session": _session_to_response(session),
        "session_complete": is_complete
    }), 200


def complete_session(user_id: int, session_id: int, data: dict):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"status": "error", "message": "Workout session not found"}), 404

    if session.status != 'completed':
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        if data.get('total_duration_seconds') is not None:
            session.total_duration_seconds = int(data['total_duration_seconds'])
        if data.get('total_calories_burned') is not None:
            session.total_calories_burned = int(data['total_calories_burned'])

        log = ActivityLog(
            user_id=user_id,
            log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
            log_type='workout',
            description=f"{session.session_name or 'Workout'} completed",
            calories_out=int(session.total_calories_burned or 0),
            duration_min=max(1, int(round((session.total_duration_seconds or 0) / 60)))
        )
        db.session.add(log)
        db.session.commit()
    else:
        log = None

    return jsonify({
        "status": "success",
        "message": "Workout session completed",
        "session": _session_to_response(session),
        "log_id": log.id if log else None
    }), 200


def reset_session(user_id: int, session_id: int):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"status": "error", "message": "Workout session not found"}), 404

    session.status = 'reset'
    session.current_exercise_index = 0
    session.completed_exercises = []
    session.total_duration_seconds = 0
    session.total_calories_burned = 0
    session.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Workout session reset",
        "session": _session_to_response(session)
    }), 200


def log_timer(user_id: int, data: dict):
    """Backward-compatible timer log entry."""
    duration_sec = int(data.get('duration_seconds', 0))
    duration_min = max(1, duration_sec // 60)

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=f"Timer: {data.get('exercise_name', 'Exercise')} ({duration_sec}s)",
        calories_out=int(data.get('calories_burned') or duration_min * 5),
        duration_min=duration_min
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Timer session logged",
        "log_id": log.id
    }), 201
