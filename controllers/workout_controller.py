from datetime import date, datetime

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.workout_plan import WorkoutPlan
from models.workout_session import WorkoutSession
from utils.workout_planner import DAY_ORDER, generate_profile_workout_plan


def _serialize_custom_plans(plans) -> list:
    enriched_days = []
    for plan in plans:
        exercises = plan.exercises or []
        total_duration = sum(int(ex.get('estimated_duration_min') or ex.get('duration_min') or 0) for ex in exercises)
        total_calories = round(sum(float(ex.get('estimated_calories_burn') or 0) for ex in exercises), 1)
        enriched_days.append({
            'day': plan.day_of_week,
            'plan_name': plan.plan_name or f'{plan.day_of_week} Workout',
            'theme': plan.plan_name or f'{plan.day_of_week} Workout',
            'is_rest_day': not bool(exercises),
            'total_duration_min': total_duration,
            'total_estimated_calories_burn': total_calories,
            'exercises': exercises
        })
    return sorted(enriched_days, key=lambda item: DAY_ORDER.index(item['day']))


def _active_session_payload(user_id: int):
    session = WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.started_at.desc()).first()
    return session.to_dict() if session else None


def get_plan(user_id: int):
    """Return a custom plan if present, otherwise the profile-driven ML plan."""
    plans = WorkoutPlan.query.filter_by(user_id=user_id).all()
    plans = sorted(plans, key=lambda item: DAY_ORDER.index(item.day_of_week) if item.day_of_week in DAY_ORDER else 99)

    if plans:
        custom_days = _serialize_custom_plans(plans)
        today_key = DAY_ORDER[datetime.utcnow().weekday()]
        today_plan = next((day for day in custom_days if day['day'] == today_key), None) or (custom_days[0] if custom_days else None)
        return jsonify({
            "status": "success",
            "source": "custom",
            "goal_label": "Custom Workout Plan",
            "goal_badge": "CUSTOM PLAN",
            "hero_image_url": next((exercise.get('demo_media_url') for exercise in (today_plan or {}).get('exercises', []) if exercise.get('demo_media_url')), None),
            "goal_eta_weeks": None,
            "total_days": len(custom_days),
            "active_days": sum(1 for day in custom_days if day['total_duration_min'] > 0),
            "total_duration_min": sum(day['total_duration_min'] for day in custom_days),
            "total_estimated_calories_burn": round(sum(day['total_estimated_calories_burn'] for day in custom_days), 1),
            "today_plan": today_plan,
            "workout_stats": {
                "exercise_count": len((today_plan or {}).get('exercises', [])),
                "minutes": (today_plan or {}).get('total_duration_min', 0),
                "calories": (today_plan or {}).get('total_estimated_calories_burn', 0)
            },
            "active_session": _active_session_payload(user_id),
            "plan": custom_days
        }), 200

    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"status": "error", "message": "Please create your health profile first"}), 404

    generated_plan = generate_profile_workout_plan(profile)
    generated_plan['active_session'] = _active_session_payload(user_id)
    return jsonify(generated_plan), 200


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
    return jsonify({
        "status": "success",
        "message": "Workout plan saved",
        "plan_id": plan.id,
        "plan_preview": {
            "day": plan.day_of_week,
            "plan_name": plan.plan_name,
            "exercises": plan.exercises or []
        }
    }), 200


def log_timer(user_id: int, data: dict):
    """Log a timer exercise session as an activity log entry."""
    duration_sec = data.get('duration_seconds', 0)
    duration_min = max(1, duration_sec // 60)

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=f"Timer: {data.get('exercise_name', 'Exercise')} ({duration_sec}s)",
        calories_out=int(duration_min * 5),
        duration_min=duration_min
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Timer session logged",
        "log_id": log.id
    }), 201


def start_session(user_id: int, data: dict):
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"status": "error", "message": "Please create your health profile first"}), 404

    generated_plan = generate_profile_workout_plan(profile)
    requested_day = data.get('day') or generated_plan.get('today_plan', {}).get('day')
    day_plan = next((day for day in generated_plan.get('days', []) if day['day'] == requested_day), generated_plan.get('today_plan'))
    if not day_plan:
        return jsonify({"status": "error", "message": "Workout day not found"}), 404

    WorkoutSession.query.filter_by(user_id=user_id, status='active').delete()
    db.session.commit()

    session = WorkoutSession(
        user_id=user_id,
        status='active',
        day=day_plan['day'],
        goal=profile.fitness_goal,
        session_title=day_plan['plan_name'],
        plan_snapshot=day_plan,
        current_exercise_index=0,
        completed_exercises=[],
        total_duration_seconds=0,
        total_calories_burned=0
    )
    db.session.add(session)
    db.session.commit()

    return jsonify({"status": "success", "session": session.to_dict()}), 201


def get_active_session(user_id: int):
    session = WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.started_at.desc()).first()
    if not session:
        return jsonify({"status": "error", "message": "No active workout session"}), 404
    return jsonify({"status": "success", "session": session.to_dict()}), 200


def complete_exercise(user_id: int, session_id: int, data: dict):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id, status='active').first()
    if not session:
        return jsonify({"status": "error", "message": "Active session not found"}), 404

    exercises = (session.plan_snapshot or {}).get('exercises', [])
    if not exercises:
        return jsonify({"status": "error", "message": "Session has no exercises"}), 400

    index = min(session.current_exercise_index or 0, len(exercises) - 1)
    exercise = exercises[index]
    duration_seconds = int(data.get('duration_seconds') or exercise.get('duration_seconds') or 0)
    calories_burned = float(data.get('calories_burned') or exercise.get('estimated_calories_burn') or 0)

    completed = session.completed_exercises or []
    completed.append({
        'index': index,
        'name': exercise.get('name'),
        'duration_seconds': duration_seconds,
        'calories_burned': calories_burned
    })
    session.completed_exercises = completed
    session.total_duration_seconds = int(session.total_duration_seconds or 0) + duration_seconds
    session.total_calories_burned = float(session.total_calories_burned or 0) + calories_burned
    session.current_exercise_index = min(index + 1, len(exercises))
    db.session.commit()

    next_exercise = exercises[session.current_exercise_index] if session.current_exercise_index < len(exercises) else None
    return jsonify({
        "status": "success",
        "session": session.to_dict(),
        "next_exercise": next_exercise,
        "finished_all": next_exercise is None
    }), 200


def complete_session(user_id: int, session_id: int, data: dict):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id, status='active').first()
    if not session:
        return jsonify({"status": "error", "message": "Active session not found"}), 404

    total_duration_seconds = int(data.get('total_duration_seconds') or session.total_duration_seconds or 0)
    total_calories_burned = float(data.get('total_calories_burned') or session.total_calories_burned or 0)
    session.total_duration_seconds = total_duration_seconds
    session.total_calories_burned = total_calories_burned
    session.status = 'completed'
    session.completed_at = datetime.utcnow()

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=session.session_title or f"{session.day} workout completed",
        calories_out=int(round(total_calories_burned)),
        duration_min=max(1, round(total_duration_seconds / 60))
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Workout completed",
        "session": session.to_dict(),
        "log_id": log.id
    }), 200


def reset_session(user_id: int, session_id: int):
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id, status='active').first()
    if not session:
        return jsonify({"status": "error", "message": "Active session not found"}), 404

    session.status = 'reset'
    session.current_exercise_index = 0
    session.completed_exercises = []
    session.total_duration_seconds = 0
    session.total_calories_burned = 0
    session.completed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"status": "success", "message": "Workout session reset"}), 200
