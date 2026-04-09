from datetime import datetime

from models.health_profile import HealthProfile
from models.workout_session import WorkoutSession
from utils.bmi_calculator import get_bmi_category
from utils.workout_templates import DAY_ORDER, build_goal_based_workout_plan


GOAL_LABELS = {
    'weight_loss': 'Lose Weight',
    'muscle_gain': 'Build Muscle',
    'maintenance': 'Get Fit',
}

GOAL_BADGES = {
    'weight_loss': 'LOSE WEIGHT',
    'muscle_gain': 'BUILD MUSCLE',
    'maintenance': 'GET FIT',
}

GOAL_HERO_IMAGES = {
    'weight_loss': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=80',
    'muscle_gain': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1200&q=80',
    'maintenance': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1200&q=80',
}

PLAN_CODE_TO_TEMPLATE = {
    1: 'mixed',
    2: 'mixed',
    3: 'cardio',
    4: 'mixed',
    5: 'cardio',
    6: 'strength',
}


def _today_day_code() -> str:
    return DAY_ORDER[datetime.utcnow().weekday()]


def _estimate_goal_eta_weeks(profile: HealthProfile) -> int:
    goal = profile.fitness_goal
    bmi = float(profile.bmi or 0)
    body_fat = float(profile.body_fat_percentage or 0)

    if goal == 'weight_loss':
        if bmi >= 32 or body_fat >= 30:
            return 20
        if bmi >= 28 or body_fat >= 25:
            return 16
        return 12

    if goal == 'muscle_gain':
        if bmi < 19:
            return 14
        if body_fat >= 24:
            return 16
        return 12

    if body_fat >= 28:
        return 12
    return 8


def _plan_code_from_profile(profile: HealthProfile) -> int:
    bmi = float(profile.bmi or 0)
    body_fat = float(profile.body_fat_percentage or 0)
    goal = profile.fitness_goal

    if goal == 'weight_loss':
        return 6 if (bmi >= 30 or body_fat >= 30) else 5
    if goal == 'muscle_gain':
        return 6 if body_fat < 24 else 4
    return 4 if body_fat < 28 else 5


def _find_active_session(user_id: int):
    return WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.created_at.desc()).first()


def build_profile_driven_workout_payload(user_id: int):
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    goal = profile.fitness_goal if profile else 'maintenance'

    detailed_plan = build_goal_based_workout_plan(goal)
    today_key = _today_day_code()
    today_plan = next((day for day in detailed_plan.get('days', []) if day.get('day') == today_key), None)
    active_session = _find_active_session(user_id)

    goal_label = GOAL_LABELS.get(goal, 'Get Fit')
    plan_code = _plan_code_from_profile(profile) if profile else 4
    template_key = PLAN_CODE_TO_TEMPLATE.get(plan_code, detailed_plan.get('template_key', 'mixed'))

    workout_stats = {
        'exercise_count': sum(len(day.get('exercises', [])) for day in detailed_plan.get('days', [])),
        'minutes': detailed_plan.get('total_duration_min', 0),
        'calories': detailed_plan.get('total_estimated_calories_burn', 0),
    }

    payload = {
        'status': 'success',
        'source': 'goal_based',
        'goal': goal,
        'goal_label': goal_label,
        'goal_badge': GOAL_BADGES.get(goal, goal_label.upper()),
        'goal_eta_weeks': _estimate_goal_eta_weeks(profile) if profile else 8,
        'hero_image_url': GOAL_HERO_IMAGES.get(goal),
        'template_key': template_key,
        'plan_code': plan_code,
        'bmi': float(profile.bmi) if profile and profile.bmi is not None else None,
        'bmi_category': get_bmi_category(float(profile.bmi)) if profile and profile.bmi is not None else None,
        'body_fat_percentage': float(profile.body_fat_percentage) if profile and profile.body_fat_percentage is not None else None,
        'body_fat_category': profile.body_fat_category if profile else None,
        'total_days': detailed_plan.get('total_days', 0),
        'active_days': detailed_plan.get('active_days', 0),
        'total_duration_min': detailed_plan.get('total_duration_min', 0),
        'total_estimated_calories_burn': detailed_plan.get('total_estimated_calories_burn', 0),
        'workout_stats': workout_stats,
        'today_plan': today_plan,
        'plan': detailed_plan.get('days', []),
        'active_session': active_session.to_dict() if active_session else None,
    }
    return payload
