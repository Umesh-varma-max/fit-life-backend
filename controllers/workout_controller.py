from datetime import date, datetime, timedelta

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.workout_plan import WorkoutPlan
from models.workout_session import WorkoutSession
from utils.workout_planner import DAY_ORDER, generate_profile_workout_plan


def _week_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def _resolve_exercise_sets(exercise: dict) -> int:
    return max(
        int(exercise.get('total_sets') or 0),
        int(exercise.get('sets') or 0),
        int((exercise.get('timer_config') or {}).get('total_sets') or 0),
        1
    )


def _normalize_exercise_timer(exercise: dict) -> dict:
    total_sets = _resolve_exercise_sets(exercise)
    set_duration_seconds = int(
        exercise.get('set_duration_seconds')
        or exercise.get('duration_seconds')
        or (exercise.get('timer_config') or {}).get('set_duration_seconds')
        or 0
    )
    rest_seconds = int(exercise.get('rest_seconds') or (exercise.get('timer_config') or {}).get('rest_seconds') or 0)
    timer_config = dict(exercise.get('timer_config') or {})
    timer_config.update({
        'total_sets': total_sets,
        'set_duration_seconds': set_duration_seconds,
        'rest_seconds': rest_seconds,
        'auto_reset_each_set': timer_config.get('auto_reset_each_set', total_sets > 1),
        'beep_on_set_complete': timer_config.get('beep_on_set_complete', True),
        'beep_on_exercise_complete': timer_config.get('beep_on_exercise_complete', True),
        'sound_cue': timer_config.get('sound_cue', 'beep')
    })

    normalized = dict(exercise)
    normalized['sets'] = total_sets
    normalized['total_sets'] = total_sets
    normalized['duration_seconds'] = set_duration_seconds
    normalized['set_duration_seconds'] = set_duration_seconds
    normalized['rest_seconds'] = rest_seconds
    normalized['timer_config'] = timer_config
    normalized.setdefault('estimated_calories_per_set', round(float(normalized.get('estimated_calories_burn') or 0) / max(total_sets, 1), 1))
    return normalized


def _normalize_plan_day(day_plan: dict | None) -> dict | None:
    if not day_plan:
        return day_plan
    normalized = dict(day_plan)
    normalized['exercises'] = [_normalize_exercise_timer(exercise) for exercise in (day_plan.get('exercises') or [])]
    return normalized


def _week_key_for_day(day_code: str, today_value: date | None = None) -> str:
    today_value = today_value or date.today()
    base = _week_start(today_value)
    try:
        offset = DAY_ORDER.index(day_code)
    except ValueError:
        offset = today_value.weekday()
    return str(base + timedelta(days=offset))


def _clear_session_progress(session: WorkoutSession, status: str = 'reset'):
    session.status = status
    session.current_exercise_index = 0
    session.completed_exercises = []
    session.total_duration_seconds = 0
    session.total_calories_burned = 0
    session.completed_at = datetime.utcnow()


def _expire_stale_sessions(user_id: int):
    active_sessions = WorkoutSession.query.filter_by(user_id=user_id, status='active').all()
    today_value = date.today()
    changed = False
    for session in active_sessions:
        started_date = session.started_at.date() if session.started_at else today_value
        stale_week = _week_start(started_date) != _week_start(today_value)
        stale_day = bool(session.day) and _week_key_for_day(session.day, started_date) != _week_key_for_day(session.day, today_value)
        if stale_week or stale_day:
            _clear_session_progress(session, status='expired')
            changed = True
    if changed:
        db.session.commit()


def _serialize_custom_plans(plans) -> list:
    enriched_days = []
    for plan in plans:
        exercises = [_normalize_exercise_timer(ex) for ex in (plan.exercises or [])]
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
    _expire_stale_sessions(user_id)
    session = WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.started_at.desc()).first()
    return session.to_dict() if session else None


def get_plan(user_id: int):
    """Return a custom plan if present, otherwise the profile-driven ML plan."""
    _expire_stale_sessions(user_id)
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
    duration_sec = int(data.get('duration_seconds', 0) or 0)
    completed_sets = int(data.get('completed_sets', 1) or 1)
    total_sets = int(data.get('total_sets', completed_sets) or completed_sets)
    duration_min = max(1, duration_sec // 60)
    description = f"Timer: {data.get('exercise_name', 'Exercise')} ({duration_sec}s)"
    if total_sets > 1:
        description += f" - {completed_sets}/{total_sets} sets"

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=description,
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
    _expire_stale_sessions(user_id)
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"status": "error", "message": "Please create your health profile first"}), 404

    generated_plan = generate_profile_workout_plan(profile)
    requested_day = data.get('day') or generated_plan.get('today_plan', {}).get('day')
    day_plan = next((day for day in generated_plan.get('days', []) if day['day'] == requested_day), generated_plan.get('today_plan'))
    if not day_plan:
        return jsonify({"status": "error", "message": "Workout day not found"}), 404
    day_plan = _normalize_plan_day(day_plan)

    set_overrides = data.get('exercise_set_overrides') or {}
    exercises = []
    for exercise in day_plan.get('exercises') or []:
        exercise_id = str(exercise.get('exercise_id') or exercise.get('name'))
        override_sets = set_overrides.get(exercise_id)
        updated = dict(exercise)
        if override_sets not in (None, ''):
            try:
                total_sets = max(1, int(override_sets))
            except (TypeError, ValueError):
                total_sets = _resolve_exercise_sets(updated)
            updated['sets'] = total_sets
            updated['total_sets'] = total_sets
            timer_config = dict(updated.get('timer_config') or {})
            timer_config['total_sets'] = total_sets
            timer_config['auto_reset_each_set'] = total_sets > 1
            updated['timer_config'] = timer_config
            updated['estimated_calories_per_set'] = round(float(updated.get('estimated_calories_burn') or 0) / max(total_sets, 1), 1)
        exercises.append(_normalize_exercise_timer(updated))
    day_plan['exercises'] = exercises

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
    _expire_stale_sessions(user_id)
    session = WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.started_at.desc()).first()
    if not session:
        return jsonify({"status": "error", "message": "No active workout session"}), 404
    return jsonify({"status": "success", "session": session.to_dict()}), 200


def _complete_set_progress(user_id: int, session_id: int, data: dict, complete_exercise_after: bool = False):
    _expire_stale_sessions(user_id)
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id, status='active').first()
    if not session:
        return jsonify({"status": "error", "message": "Active session not found"}), 404

    exercises = (session.plan_snapshot or {}).get('exercises', [])
    if not exercises:
        return jsonify({"status": "error", "message": "Session has no exercises"}), 400

    index = min(session.current_exercise_index or 0, len(exercises) - 1)
    exercise = _normalize_exercise_timer(exercises[index])
    total_sets = _resolve_exercise_sets(exercise)
    completed = list(session.completed_exercises or [])
    completed_for_exercise = [entry for entry in completed if int(entry.get('exercise_index', entry.get('index', -1))) == index]
    current_set_number = len(completed_for_exercise) + 1
    if complete_exercise_after:
        target_set_number = total_sets
    else:
        target_set_number = min(max(int(data.get('set_number') or current_set_number), 1), total_sets)

    duration_seconds = int(
        data.get('duration_seconds')
        or exercise.get('set_duration_seconds')
        or exercise.get('duration_seconds')
        or 0
    )
    calories_burned = float(
        data.get('calories_burned')
        or exercise.get('estimated_calories_per_set')
        or (float(exercise.get('estimated_calories_burn') or 0) / max(total_sets, 1))
        or 0
    )

    existing_set_numbers = {int(entry.get('set_number', 0)) for entry in completed_for_exercise}
    if target_set_number in existing_set_numbers:
        return jsonify({"status": "error", "message": "This set is already marked complete"}), 409

    completed.append({
        'index': index,
        'exercise_index': index,
        'set_number': target_set_number,
        'total_sets': total_sets,
        'name': exercise.get('name'),
        'duration_seconds': duration_seconds,
        'calories_burned': calories_burned
    })
    session.completed_exercises = completed
    session.total_duration_seconds = int(session.total_duration_seconds or 0) + duration_seconds
    session.total_calories_burned = float(session.total_calories_burned or 0) + calories_burned
    finished_exercise = target_set_number >= total_sets
    if finished_exercise:
        session.current_exercise_index = min(index + 1, len(exercises))
    else:
        session.current_exercise_index = index
    db.session.commit()

    remaining_sets = max(total_sets - target_set_number, 0)
    next_exercise = exercises[session.current_exercise_index] if session.current_exercise_index < len(exercises) else None
    timer_signal = {
        "should_play_sound": True,
        "sound_cue": "beep",
        "reason": "exercise_complete" if finished_exercise else "set_complete",
        "repeat_count": 2 if finished_exercise else 1
    }
    return jsonify({
        "status": "success",
        "session": session.to_dict(),
        "completed_set": {
            "exercise_index": index,
            "set_number": target_set_number,
            "total_sets": total_sets,
            "remaining_sets": remaining_sets
        },
        "finished_exercise": finished_exercise,
        "next_exercise": next_exercise,
        "finished_all": next_exercise is None,
        "timer_reset": {
            "should_reset": True,
            "next_duration_seconds": int(next_exercise.get('set_duration_seconds') or next_exercise.get('duration_seconds') or 0) if finished_exercise and next_exercise else int(exercise.get('set_duration_seconds') or exercise.get('duration_seconds') or 0),
            "rest_seconds": int(exercise.get('rest_seconds') or 0),
            "auto_reset_each_set": True
        },
        "timer_signal": timer_signal
    }), 200


def complete_set(user_id: int, session_id: int, data: dict):
    return _complete_set_progress(user_id, session_id, data, complete_exercise_after=False)


def complete_exercise(user_id: int, session_id: int, data: dict):
    return _complete_set_progress(user_id, session_id, data, complete_exercise_after=True)


def complete_session(user_id: int, session_id: int, data: dict):
    _expire_stale_sessions(user_id)
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
    _expire_stale_sessions(user_id)
    session = WorkoutSession.query.filter_by(id=session_id, user_id=user_id, status='active').first()
    if not session:
        return jsonify({"status": "error", "message": "Active session not found"}), 404

    _clear_session_progress(session, status='reset')
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Workout session reset",
        "timer_signal": {
            "should_play_sound": False,
            "sound_cue": "beep",
            "reason": "manual_reset",
            "repeat_count": 0
        }
    }), 200
