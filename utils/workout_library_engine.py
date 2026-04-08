from datetime import date
from math import ceil

from models.body_metric_reference import BodyMetricReference
from models.exercise_library import ExerciseLibrary
from utils.bmi_calculator import get_bmi_category
from utils.workout_templates import DAY_ORDER, build_goal_based_workout_plan


GOAL_LABELS = {
    'weight_loss': 'Lose Weight',
    'muscle_gain': 'Muscle Growth',
    'maintenance': 'Get Fit'
}

GOAL_BADGES = {
    'weight_loss': 'LOSE WEIGHT',
    'muscle_gain': 'BUILD MUSCLE',
    'maintenance': 'STAY FIT'
}

GOAL_HERO_IMAGES = {
    'weight_loss': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=80',
    'muscle_gain': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1200&q=80',
    'maintenance': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1200&q=80'
}

GOAL_DAY_BLUEPRINTS = {
    'weight_loss': [
        {'day': 'Mon', 'title': 'Core Burner', 'filters': ['waist', 'abs', 'cardio'], 'count': 3},
        {'day': 'Tue', 'title': 'Lower Body Burn', 'filters': ['upper legs', 'lower legs', 'glutes'], 'count': 3},
        {'day': 'Wed', 'title': 'Active Recovery', 'filters': ['waist', 'cardio'], 'count': 2},
        {'day': 'Thu', 'title': 'Fat Loss Circuit', 'filters': ['cardio', 'waist', 'chest'], 'count': 3},
        {'day': 'Fri', 'title': 'Cardio + Core', 'filters': ['waist', 'cardio'], 'count': 3},
        {'day': 'Sat', 'title': 'Full Body Burn', 'filters': ['chest', 'back', 'upper legs'], 'count': 3},
        {'day': 'Sun', 'title': 'Recovery Flow', 'filters': ['waist'], 'count': 2},
    ],
    'muscle_gain': [
        {'day': 'Mon', 'title': 'Chest + Triceps', 'filters': ['chest', 'upper arms'], 'count': 4},
        {'day': 'Tue', 'title': 'Back + Biceps', 'filters': ['back', 'lower arms'], 'count': 4},
        {'day': 'Wed', 'title': 'Leg Day', 'filters': ['upper legs', 'lower legs'], 'count': 4},
        {'day': 'Thu', 'title': 'Shoulders + Core', 'filters': ['shoulders', 'waist'], 'count': 4},
        {'day': 'Fri', 'title': 'Power Upper Body', 'filters': ['chest', 'back', 'shoulders'], 'count': 4},
        {'day': 'Sat', 'title': 'Full Body Strength', 'filters': ['upper legs', 'chest', 'back'], 'count': 4},
        {'day': 'Sun', 'title': 'Recovery Mobility', 'filters': ['waist'], 'count': 2},
    ],
    'maintenance': [
        {'day': 'Mon', 'title': 'Balanced Full Body', 'filters': ['chest', 'upper legs', 'waist'], 'count': 3},
        {'day': 'Tue', 'title': 'Cardio & Core', 'filters': ['cardio', 'waist'], 'count': 3},
        {'day': 'Wed', 'title': 'Upper Body Mix', 'filters': ['chest', 'back', 'shoulders'], 'count': 3},
        {'day': 'Thu', 'title': 'Mobility Day', 'filters': ['waist'], 'count': 2},
        {'day': 'Fri', 'title': 'Lower Body Mix', 'filters': ['upper legs', 'lower legs', 'glutes'], 'count': 3},
        {'day': 'Sat', 'title': 'Conditioning Day', 'filters': ['cardio', 'chest', 'back'], 'count': 3},
        {'day': 'Sun', 'title': 'Recovery Flow', 'filters': ['waist'], 'count': 2},
    ]
}

ACTIVE_RECOVERY_DAY_TITLES = {'Active Recovery', 'Recovery Flow', 'Mobility Day', 'Recovery Mobility'}


def _today_day_code() -> str:
    return DAY_ORDER[date.today().weekday()]


def _reference_plan_tier(profile) -> int:
    base_query = BodyMetricReference.query.filter_by(
        source_dataset='bfp',
        gender=(profile.gender or '').title()
    )
    candidates = base_query.all()
    target_bmi = float(profile.bmi or 0)
    target_bfp = float(profile.body_fat_percentage or 0)
    target_age = int(profile.age or 0)

    if not candidates:
        candidates = BodyMetricReference.query.filter_by(source_dataset='bmi', gender=(profile.gender or '').title()).all()

    if not candidates:
        if target_bmi >= 35:
            return 7
        if target_bmi >= 30:
            return 6
        if target_bmi >= 25:
            return 5
        if target_bmi >= 18.5:
            return 4
        return 2

    def score(item):
        bmi_gap = abs(float(item.bmi or 0) - target_bmi)
        age_gap = abs(int(item.age or 0) - target_age) / 10.0
        bfp_gap = abs(float(item.body_fat_percentage or 0) - target_bfp) if item.body_fat_percentage is not None else 0
        return bmi_gap + age_gap + (bfp_gap / 5.0)

    nearest = min(candidates, key=score)
    return int(nearest.exercise_recommendation_plan or 4)


def _goal_eta_weeks(profile) -> int:
    bmi = float(profile.bmi or 0)
    bfp = float(profile.body_fat_percentage or 0)

    if profile.fitness_goal == 'weight_loss':
        return max(6, ceil(max(0, bmi - 23.5) * 2.5 + max(0, bfp - 24) / 4))
    if profile.fitness_goal == 'muscle_gain':
        return max(8, ceil(max(0, 22 - bmi) * 4 + 8))
    return max(6, ceil(abs(bmi - 22.5) * 2 + 6))


def _normalize_text_list(values):
    return [str(value).strip().lower() for value in (values or []) if str(value).strip()]


def _exercise_matches(exercise: ExerciseLibrary, terms: list[str]) -> bool:
    body_parts = _normalize_text_list(exercise.body_parts)
    target_muscles = _normalize_text_list(exercise.target_muscles)
    keywords = _normalize_text_list(exercise.keywords)
    haystack = ' '.join(body_parts + target_muscles + keywords + [exercise.name.lower()])
    return any(term in haystack for term in terms)


def _exercise_duration_seconds(exercise_type: str, plan_tier: int, day_title: str) -> int:
    if day_title in ACTIVE_RECOVERY_DAY_TITLES:
        return 45 * 60
    if (exercise_type or '').upper() == 'CARDIO':
        return max(60, (10 + plan_tier * 2) * 60)
    return 60


def _exercise_prescription(goal: str, exercise: ExerciseLibrary, plan_tier: int, day_title: str) -> dict:
    is_cardio = (exercise.exercise_type or '').upper() == 'CARDIO' or 'cardio' in ' '.join(_normalize_text_list(exercise.body_parts))
    if day_title in ACTIVE_RECOVERY_DAY_TITLES:
        duration_seconds = 8 * 60 if not is_cardio else 20 * 60
        rest_seconds = 30
        sets = 1
        reps = 0
    elif is_cardio or goal == 'weight_loss':
        duration_seconds = _exercise_duration_seconds(exercise.exercise_type, plan_tier, day_title)
        rest_seconds = 30 if goal == 'weight_loss' else 45
        sets = 1
        reps = 0
    else:
        base_sets = 3 if goal == 'maintenance' else 4
        sets = min(5, base_sets + max(0, plan_tier - 4))
        reps = 12 if goal == 'maintenance' else 10
        duration_seconds = 60
        rest_seconds = 75 if goal == 'muscle_gain' else 45

    minutes = max(1, round((sets * duration_seconds + max(0, sets - 1) * rest_seconds) / 60))
    calories_per_min = 6.0 if goal == 'weight_loss' else 5.5 if goal == 'maintenance' else 6.5
    calories = int(round(minutes * calories_per_min))
    muscle_group = ', '.join((exercise.target_muscles or exercise.body_parts or ['full body'])[:2])

    return {
        'external_id': exercise.external_id,
        'name': exercise.name,
        'sets': sets,
        'reps': reps,
        'duration_seconds': duration_seconds,
        'rest_seconds': rest_seconds,
        'duration_min': minutes,
        'muscle_group': muscle_group.title(),
        'description': exercise.overview or f'{exercise.name} for {muscle_group}.',
        'instructions': exercise.instructions or [],
        'exercise_tips': exercise.exercise_tips or [],
        'body_parts': exercise.body_parts or [],
        'target_muscles': exercise.target_muscles or [],
        'secondary_muscles': exercise.secondary_muscles or [],
        'equipments': exercise.equipments or [],
        'gif_url': exercise.gif_url,
        'image_url': exercise.image_url,
        'video_url': exercise.video_url,
        'demo_media_url': exercise.gif_url or exercise.image_url or exercise.video_url,
        'has_demo_media': bool(exercise.gif_url or exercise.image_url or exercise.video_url),
        'media_fallback_text': exercise.overview or f'{exercise.name} exercise details are available below.',
        'estimated_calories_burn': calories,
        'posture': exercise.name,
        'posture_cues': (exercise.exercise_tips or [])[:3]
    }


def _select_exercises(filters: list[str], count: int) -> list[ExerciseLibrary]:
    all_exercises = ExerciseLibrary.query.order_by(ExerciseLibrary.name.asc()).all()
    if not all_exercises:
        return []

    selected = []
    used_ids = set()
    for term in filters:
        for exercise in all_exercises:
            if exercise.id in used_ids:
                continue
            if _exercise_matches(exercise, [term]):
                selected.append(exercise)
                used_ids.add(exercise.id)
                if len(selected) >= count:
                    return selected

    for exercise in all_exercises:
        if exercise.id in used_ids:
            continue
        selected.append(exercise)
        if len(selected) >= count:
            break
    return selected


def _build_library_day(profile, blueprint: dict, plan_tier: int) -> dict:
    exercises = _select_exercises(blueprint['filters'], blueprint['count'])
    if not exercises:
        return None

    prescribed = [
        _exercise_prescription(profile.fitness_goal, exercise, plan_tier, blueprint['title'])
        for exercise in exercises
    ]
    total_duration_min = sum(item['duration_min'] for item in prescribed)
    total_calories = sum(item['estimated_calories_burn'] for item in prescribed)

    return {
        'day': blueprint['day'],
        'plan_name': f"{blueprint['day']} {GOAL_LABELS.get(profile.fitness_goal, 'Workout')} Plan",
        'session_title': blueprint['title'],
        'goal_label': GOAL_LABELS.get(profile.fitness_goal, 'Get Fit'),
        'total_duration_min': total_duration_min,
        'total_estimated_calories_burn': total_calories,
        'exercise_count': len(prescribed),
        'exercises': prescribed
    }


def generate_personalized_workout_plan(profile) -> dict:
    """Generate a profile-aware workout plan using imported exercise library data."""
    if profile is None:
        fallback = build_goal_based_workout_plan('maintenance')
        return {
            **fallback,
            'goal_label': GOAL_LABELS['maintenance'],
            'goal_badge': GOAL_BADGES['maintenance'],
            'hero_image_url': GOAL_HERO_IMAGES['maintenance'],
            'today_day': _today_day_code(),
            'today_plan': next((day for day in fallback['days'] if day['day'] == _today_day_code()), None),
            'recommended_plan_tier': 4,
            'goal_eta_weeks': 8,
            'bmi_category': None,
            'body_fat_category': None,
            'has_library_data': False
        }

    blueprints = GOAL_DAY_BLUEPRINTS.get(profile.fitness_goal, GOAL_DAY_BLUEPRINTS['maintenance'])
    plan_tier = _reference_plan_tier(profile)
    days = [_build_library_day(profile, blueprint, plan_tier) for blueprint in blueprints]
    days = [day for day in days if day is not None]

    if not days:
        fallback = build_goal_based_workout_plan(profile.fitness_goal)
        return {
            **fallback,
            'goal_label': GOAL_LABELS.get(profile.fitness_goal, 'Get Fit'),
            'goal_badge': GOAL_BADGES.get(profile.fitness_goal, 'STAY FIT'),
            'hero_image_url': GOAL_HERO_IMAGES.get(profile.fitness_goal, GOAL_HERO_IMAGES['maintenance']),
            'today_day': _today_day_code(),
            'today_plan': next((day for day in fallback['days'] if day['day'] == _today_day_code()), None),
            'recommended_plan_tier': plan_tier,
            'goal_eta_weeks': _goal_eta_weeks(profile),
            'bmi_category': get_bmi_category(float(profile.bmi or 0)),
            'body_fat_category': profile.body_fat_category,
            'has_library_data': False
        }

    total_duration = sum(day['total_duration_min'] for day in days)
    total_calories = sum(day['total_estimated_calories_burn'] for day in days)
    today_day = _today_day_code()
    today_plan = next((day for day in days if day['day'] == today_day), days[0] if days else None)

    return {
        'goal': profile.fitness_goal,
        'goal_label': GOAL_LABELS.get(profile.fitness_goal, 'Get Fit'),
        'goal_badge': GOAL_BADGES.get(profile.fitness_goal, 'STAY FIT'),
        'hero_image_url': GOAL_HERO_IMAGES.get(profile.fitness_goal, GOAL_HERO_IMAGES['maintenance']),
        'template_key': f'library_{profile.fitness_goal}',
        'recommended_plan_tier': plan_tier,
        'goal_eta_weeks': _goal_eta_weeks(profile),
        'bmi_category': get_bmi_category(float(profile.bmi or 0)),
        'body_fat_category': profile.body_fat_category,
        'total_days': len(days),
        'active_days': sum(1 for day in days if day['total_duration_min'] > 0),
        'total_duration_min': total_duration,
        'total_estimated_calories_burn': total_calories,
        'today_day': today_day,
        'today_plan': today_plan,
        'days': days,
        'has_library_data': True
    }
