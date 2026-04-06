from datetime import date

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.workout_plan import WorkoutPlan
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


def get_plan(user_id: int):
    """Return a custom plan if present, otherwise a goal-based weekly workout plan."""
    plans = WorkoutPlan.query.filter_by(user_id=user_id).all()
    plans = sorted(
        plans,
        key=lambda item: DAY_ORDER.index(item.day_of_week) if item.day_of_week in DAY_ORDER else 99
    )

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
    goal = profile.fitness_goal if profile else 'maintenance'
    generated_plan = build_goal_based_workout_plan(goal)

    return jsonify({
        "status": "success",
        "source": "goal_based",
        "goal": generated_plan['goal'],
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
