from datetime import date

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.workout_plan import WorkoutPlan
from utils.ai_structured import groq_json_completion
from utils.goal_presets import goal_label, normalize_goal
from utils.workout_templates import DAY_ORDER, build_goal_based_workout_plan, build_workout_day


def _serialize_custom_plans(plans) -> list:
    """Enrich saved workout plans with totals and posture guidance."""
    enriched_days = [
        build_workout_day(plan.day_of_week, plan.exercises or [], plan.plan_name)
        for plan in plans
    ]
    return sorted(enriched_days, key=lambda item: DAY_ORDER.index(item['day']))


def _plan_summary(enriched_plan: list) -> dict:
    """Calculate weekly totals from enriched daily plans."""
    return {
        'total_days': len(enriched_plan),
        'active_days': sum(1 for day in enriched_plan if day['total_duration_min'] > 0),
        'total_duration_min': sum(day['total_duration_min'] for day in enriched_plan),
        'total_estimated_calories_burn': sum(day['total_estimated_calories_burn'] for day in enriched_plan)
    }


def _build_ai_workout_prompt(goal: str, custom_prompt: str = None) -> str:
    base_prompt = (
        f"Generate a weekly workout plan for the goal '{goal_label(goal)}'. "
        "Return pure JSON only with this exact structure: "
        "{\"goal_label\": string, \"days\": [{\"day\": string, \"focus_area\": string, "
        "\"exercises\": [{\"name\": string, \"sets\": number, \"reps\": number, "
        "\"duration_seconds\": number, \"rest_seconds\": number, \"muscle_group\": string, "
        "\"description\": string, \"animation_category\": string, \"estimated_calories_burn\": number}]}]}. "
        "Use seven days from Mon to Sun. Keep exercises realistic for a fitness app."
    )
    return custom_prompt.strip() if custom_prompt else base_prompt


def _fallback_ai_workout(goal: str) -> dict:
    generated_plan = build_goal_based_workout_plan(goal)
    return {
        "goal_label": goal_label(goal),
        "days": generated_plan["days"]
    }


def generate_workout_plan(user_id: int, goal: str = None, prompt_text: str = None):
    """Generate a weekly AI workout plan for supported frontend goals."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    canonical_goal = normalize_goal(goal or (profile.fitness_goal if profile else None))

    try:
        ai_payload = groq_json_completion(
            system_prompt=(
                "You are a fitness planning engine for FitLife. "
                "Return JSON only. No markdown. No prose outside JSON."
            ),
            user_prompt=_build_ai_workout_prompt(canonical_goal, prompt_text)
        )
        days = []
        for item in ai_payload.get("days", []):
            day_name = item.get("day", "Mon")
            exercises = item.get("exercises", [])
            day_payload = build_workout_day(day_name, exercises, f"{day_name} {goal_label(canonical_goal)} Plan")
            day_payload["focus_area"] = item.get("focus_area") or day_payload["focus_area"]
            days.append(day_payload)
        payload = {
            "goal": canonical_goal,
            "goal_label": ai_payload.get("goal_label") or goal_label(canonical_goal),
            "source": "ai",
            "plan": days or _fallback_ai_workout(canonical_goal)["days"]
        }
    except Exception:
        payload = {
            "goal": canonical_goal,
            "goal_label": goal_label(canonical_goal),
            "source": "fallback_template",
            "plan": _fallback_ai_workout(canonical_goal)["days"]
        }

    summary = _plan_summary(payload["plan"])
    payload.update(summary)
    payload["prompt_used"] = _build_ai_workout_prompt(canonical_goal, prompt_text)
    return jsonify({"status": "success", **payload}), 200


def get_plan(user_id: int, goal: str = None):
    """Return a custom plan if present, otherwise a goal-based weekly workout plan."""
    plans = WorkoutPlan.query.filter_by(user_id=user_id).order_by(
        db.case(
            {'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7},
            value=WorkoutPlan.day_of_week
        )
    ).all()

    if plans:
        enriched_plan = _serialize_custom_plans(plans)
        summary = _plan_summary(enriched_plan)
        return jsonify({
            "status": "success",
            "source": "custom",
            **summary,
            "plan": enriched_plan
        }), 200

    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    canonical_goal = normalize_goal(goal or (profile.fitness_goal if profile else None))
    generated_plan = build_goal_based_workout_plan(canonical_goal)

    return jsonify({
        "status": "success",
        "source": "goal_based",
        "goal": generated_plan['goal'],
        "goal_label": goal_label(canonical_goal),
        "template_key": generated_plan['template_key'],
        "total_days": generated_plan['total_days'],
        "active_days": generated_plan['active_days'],
        "total_duration_min": generated_plan['total_duration_min'],
        "total_estimated_calories_burn": generated_plan['total_estimated_calories_burn'],
        "plan": generated_plan['days']
    }), 200


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


def log_timer(user_id: int, data: dict):
    """Log a timer exercise session as an activity log entry."""
    duration_sec = int(data.get('duration_seconds', 0) or 0)
    duration_min = max(1, duration_sec // 60 if duration_sec else 1)

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=f"Timer: {data.get('exercise_name', 'Exercise')} ({duration_sec}s)",
        calories_out=int(data.get('estimated_calories_burn') or (duration_min * 5)),
        duration_min=duration_min,
        details={
            "entry_type": "timer_session",
            "exercise_name": data.get('exercise_name', 'Exercise'),
            "sets": int(data.get('sets') or 0),
            "reps": int(data.get('reps') or 0),
            "duration_seconds": duration_sec,
            "goal": normalize_goal(data.get('goal') or ''),
            "logged_at": data.get('log_date') or date.today().isoformat()
        }
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Timer session logged",
        "log_id": log.id
    }), 201


def log_completed_workout(user_id: int, data: dict):
    """Persist a completed multi-exercise workout session."""
    exercises = data.get('exercises') or []
    total_duration_seconds = int(data.get('total_duration_seconds') or sum(
        int(exercise.get('duration_seconds') or 0) + int(exercise.get('rest_seconds') or 0)
        for exercise in exercises
    ))
    total_duration_min = max(1, round(total_duration_seconds / 60))
    estimated_calories = int(data.get('estimated_calories_burn') or sum(
        int(exercise.get('estimated_calories_burn') or 0) for exercise in exercises
    ) or total_duration_min * 5)
    canonical_goal = normalize_goal(data.get('goal') or '')

    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(data['log_date']) if data.get('log_date') else date.today(),
        log_type='workout',
        description=f"Workout Complete: {goal_label(canonical_goal)}",
        calories_out=estimated_calories,
        duration_min=total_duration_min,
        details={
            "entry_type": "completed_workout",
            "goal": canonical_goal,
            "goal_label": goal_label(canonical_goal),
            "exercise_count": len(exercises),
            "exercises": exercises,
            "total_duration_seconds": total_duration_seconds,
            "estimated_calories_burn": estimated_calories,
            "logged_at": data.get('log_date') or date.today().isoformat()
        }
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Workout complete log saved",
        "log_id": log.id,
        "summary": log.details
    }), 201
