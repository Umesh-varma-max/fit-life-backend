from datetime import date, datetime

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.workout_plan import WorkoutPlan
from models.workout_session import WorkoutSession
from utils.workout_profile_engine import build_profile_driven_workout_payload
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
        'total_estimated_calories_burn': sum(day['total_estimated_calories_burn'] for day in enriched_plan),
        'workout_stats': {
            'exercise_count': sum(len(day['exercises']) for day in enriched_plan),
            'minutes': sum(day['total_duration_min'] for day in enriched_plan),
            'calories': sum(day['total_estimated_calories_burn'] for day in enriched_plan),
        }
    }


def _active_session(user_id: int):
    return WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.created_at.desc()).first()


def get_plan(user_id: int):
    base_payload = build_profile_driven_workout_payload(user_id)
    plans = WorkoutPlan.query.filter_by(user_id=user_id).all()
    plans = sorted(
        plans,
        key=lambda item: DAY_ORDER.index(item.day_of_week) if item.day_of_week in DAY_ORDER else 99
    )

    if plans:
        enriched_plan = _serialize_custom_plans(plans)
        summary = _plan_summary(enriched_plan)
        today_code = DAY_ORDER[datetime.utcnow().weekday()]
        today_plan = next((day for day in enriched_plan if day['day'] == today_code), None)
        return jsonify({
            **base_payload,
            "source": "custom",
            **summary,
            "today_plan": today_plan,
            "plan": enriched_plan,
            "active_session": _active_session(user_id).to_dict() if _active_session(user_id) else None
        }), 200

    return jsonify(base_payload), 200


def save_plan(user_id: int, data: dict):
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
    active = _active_session(user_id)
    if active:
        return jsonify({"status": "success", "session": active.to_dict(), "message": "Workout session resumed"}), 200

    payload = build_profile_driven_workout_payload(user_id)
    target_day = data.get('day') or (payload.get('today_plan') or {}).get('day')
    today_plan = next((day for day in payload.get('plan', []) if day.get('day') == target_day), payload.get('today_plan'))
    if not today_plan:
        return jsonify({"status": "error", "message": "No workout plan available to start"}), 404

    session = WorkoutSession(
        user_id=user_id,
        day_of_week=today_plan.get('day'),
        goal_label=payload.get('goal_label'),
        goal_key=payload.get('goal'),
        status='active',
        current_exercise_index=0,
        exercises=today_plan.get('exercises', []),
        completed_exercises=[],
        total_duration_seconds=0,
        total_calories_burned=0
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({"status": "success", "message": "Workout session started", "session": session.to_dict()}), 201


def get_active_session(user_id: int):
    active = _active_session(user_id)
    if not active:
        return jsonify({"status": "error", "message": "No active workout session"}), 404
    return jsonify({"status": "success", "session": active.to_dict()}), 200


def complete_session_exercise(user_id: int, session_id: int, data: dict):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session or session.status != 'active':
        return jsonify({"status": "error", "message": "Active workout session not found"}), 404

    exercises = session.exercises or []
    if not exercises or session.current_exercise_index >= len(exercises):
        return jsonify({"status": "error", "message": "No remaining exercises in this session"}), 400

    current = exercises[session.current_exercise_index]
    completed = list(session.completed_exercises or [])
    completed_entry = dict(current)
    completed_entry['logged_duration_seconds'] = int(data.get('duration_seconds') or current.get('duration_seconds') or 0)
    completed_entry['logged_calories_burned'] = int(data.get('calories_burned') or current.get('estimated_calories_burn') or 0)
    completed.append(completed_entry)

    session.completed_exercises = completed
    session.total_duration_seconds += completed_entry['logged_duration_seconds']
    session.total_calories_burned += completed_entry['logged_calories_burned']
    session.current_exercise_index += 1
    db.session.commit()

    is_complete = session.current_exercise_index >= len(exercises)
    next_exercise = None if is_complete else exercises[session.current_exercise_index]
    return jsonify({
        "status": "success",
        "message": "Exercise marked complete",
        "session": session.to_dict(),
        "next_exercise": next_exercise,
        "is_workout_complete": is_complete
    }), 200


def complete_session(user_id: int, session_id: int, data: dict):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return jsonify({"status": "error", "message": "Workout session not found"}), 404

    if session.status == 'completed':
        return jsonify({"status": "success", "message": "Workout already completed", "session": session.to_dict()}), 200

    if data.get('total_duration_seconds') is not None:
        session.total_duration_seconds = int(data.get('total_duration_seconds') or session.total_duration_seconds)
    if data.get('total_calories_burned') is not None:
        session.total_calories_burned = int(data.get('total_calories_burned') or session.total_calories_burned)

    session.status = 'completed'
    session.completed_at = datetime.utcnow()
    db.session.commit()

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=f"{session.goal_label or 'Workout'} session completed",
        calories_out=int(round(session.total_calories_burned)),
        duration_min=max(1, int(round(session.total_duration_seconds / 60)))
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Workout completed",
        "session": session.to_dict(),
        "workout_log": {
            "logged": True,
            "log_id": log.id
        }
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
    db.session.commit()
    return jsonify({"status": "success", "message": "Workout session reset"}), 200


def log_timer(user_id: int, data: dict):
    duration_sec = int(data.get('duration_seconds') or 0)
    duration_min = max(1, duration_sec // 60)

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=f"Timer: {data.get('exercise_name', 'Exercise')} ({duration_sec}s)",
        calories_out=int(data.get('calories_burned') or (duration_min * 5)),
        duration_min=duration_min
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Timer session logged",
        "log_id": log.id
    }), 201
