"""Profile-driven workout planning built on the exercise library."""

from __future__ import annotations

from datetime import datetime

from models.exercise_library import ExerciseLibrary
from utils.goal_achievement_model import estimate_goal_timeline


DAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

GOAL_TRACKS = {
    'weight_loss': [
        {'day': 'Mon', 'title': 'Metabolic Lower Body', 'categories': ['strength', 'cardio'], 'muscles': ['quadriceps', 'glutes', 'hamstrings'], 'style': 'circuit'},
        {'day': 'Tue', 'title': 'Conditioning Core', 'categories': ['cardio', 'plyometrics'], 'muscles': ['abdominals', 'lower back'], 'style': 'interval'},
        {'day': 'Wed', 'title': 'Upper Body Burn', 'categories': ['strength'], 'muscles': ['chest', 'back', 'shoulders'], 'style': 'superset'},
        {'day': 'Thu', 'title': 'Recovery Mobility', 'categories': ['stretching'], 'muscles': ['hamstrings', 'glutes', 'abdominals'], 'style': 'mobility'},
        {'day': 'Fri', 'title': 'Full Body Fat-Loss', 'categories': ['strength', 'cardio'], 'muscles': ['quadriceps', 'chest', 'abdominals'], 'style': 'circuit'},
        {'day': 'Sat', 'title': 'Endurance Finish', 'categories': ['cardio', 'plyometrics'], 'muscles': ['calves', 'glutes', 'abdominals'], 'style': 'interval'},
        {'day': 'Sun', 'title': 'Recovery Reset', 'categories': ['stretching'], 'muscles': ['hamstrings', 'lower back'], 'style': 'recovery'}
    ],
    'muscle_gain': [
        {'day': 'Mon', 'title': 'Push Strength', 'categories': ['strength'], 'muscles': ['chest', 'shoulders', 'triceps'], 'style': 'strength'},
        {'day': 'Tue', 'title': 'Lower Body Power', 'categories': ['strength'], 'muscles': ['quadriceps', 'hamstrings', 'glutes'], 'style': 'strength'},
        {'day': 'Wed', 'title': 'Mobility Reset', 'categories': ['stretching'], 'muscles': ['lower back', 'hamstrings'], 'style': 'mobility'},
        {'day': 'Thu', 'title': 'Pull Hypertrophy', 'categories': ['strength'], 'muscles': ['lats', 'middle back', 'biceps'], 'style': 'strength'},
        {'day': 'Fri', 'title': 'Full Body Mass', 'categories': ['strength'], 'muscles': ['quadriceps', 'chest', 'abdominals'], 'style': 'strength'},
        {'day': 'Sat', 'title': 'Athletic Accessories', 'categories': ['plyometrics', 'strength'], 'muscles': ['shoulders', 'abdominals', 'calves'], 'style': 'accessory'},
        {'day': 'Sun', 'title': 'Recovery Reset', 'categories': ['stretching'], 'muscles': ['hamstrings', 'lower back'], 'style': 'recovery'}
    ],
    'maintenance': [
        {'day': 'Mon', 'title': 'Balanced Strength', 'categories': ['strength'], 'muscles': ['chest', 'shoulders', 'quadriceps'], 'style': 'strength'},
        {'day': 'Tue', 'title': 'Steady Cardio', 'categories': ['cardio'], 'muscles': ['abdominals', 'calves'], 'style': 'steady'},
        {'day': 'Wed', 'title': 'Mobility & Core', 'categories': ['stretching', 'strength'], 'muscles': ['abdominals', 'lower back'], 'style': 'mobility'},
        {'day': 'Thu', 'title': 'Athletic Mix', 'categories': ['strength', 'plyometrics'], 'muscles': ['glutes', 'shoulders', 'abdominals'], 'style': 'mixed'},
        {'day': 'Fri', 'title': 'Conditioning Blend', 'categories': ['cardio', 'strength'], 'muscles': ['quadriceps', 'chest', 'back'], 'style': 'mixed'},
        {'day': 'Sat', 'title': 'Outdoor Engine', 'categories': ['cardio', 'plyometrics'], 'muscles': ['calves', 'hamstrings'], 'style': 'steady'},
        {'day': 'Sun', 'title': 'Recovery Reset', 'categories': ['stretching'], 'muscles': ['hamstrings', 'lower back'], 'style': 'recovery'}
    ]
}

LEVEL_ORDER = {'beginner': 1, 'intermediate': 2, 'expert': 3}
PROFILE_LEVEL_LIMIT = {'sedentary': 1, 'light': 1, 'moderate': 2, 'active': 3}
STYLE_REP_SCHEMES = {
    'strength': {'sets': 4, 'reps': 10, 'rest_seconds': 75, 'duration_seconds': 45},
    'superset': {'sets': 3, 'reps': 12, 'rest_seconds': 45, 'duration_seconds': 40},
    'circuit': {'sets': 3, 'reps': 15, 'rest_seconds': 30, 'duration_seconds': 45},
    'interval': {'sets': 4, 'reps': 0, 'rest_seconds': 30, 'duration_seconds': 50},
    'steady': {'sets': 1, 'reps': 0, 'rest_seconds': 0, 'duration_seconds': 600},
    'mobility': {'sets': 2, 'reps': 0, 'rest_seconds': 20, 'duration_seconds': 60},
    'recovery': {'sets': 2, 'reps': 0, 'rest_seconds': 20, 'duration_seconds': 45},
    'accessory': {'sets': 3, 'reps': 12, 'rest_seconds': 45, 'duration_seconds': 40},
    'mixed': {'sets': 3, 'reps': 12, 'rest_seconds': 45, 'duration_seconds': 45}
}
HERO_IMAGES = {
    'weight_loss': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=1200&q=80',
    'muscle_gain': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1200&q=80',
    'maintenance': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1200&q=80'
}


def _today_key():
    return DAY_ORDER[datetime.utcnow().weekday()]


def _normalize(values):
    return {str(value).strip().lower() for value in (values or []) if value}


def _exercise_score(exercise, categories, muscles, profile_level_limit):
    score = 0.0
    if (exercise.category or '').lower() in categories:
        score += 4.0
    primary = _normalize(exercise.primary_muscles)
    secondary = _normalize(exercise.secondary_muscles)
    score += len(primary.intersection(muscles)) * 2.5
    if secondary.intersection(muscles):
        score += 1.5
    exercise_level = LEVEL_ORDER.get((exercise.level or 'beginner').lower(), 2)
    if exercise_level <= profile_level_limit:
        score += 1.5
    else:
        score -= (exercise_level - profile_level_limit) * 2
    equipment = (exercise.equipment or '').lower()
    if equipment in {'body only', 'exercise ball', 'dumbbell', 'bands', 'kettlebells'}:
        score += 0.75
    if not exercise.image_url and not exercise.demo_media_url:
        score -= 1.0
    return score


def _select_exercises(profile, plan_day, limit=5):
    categories = _normalize(plan_day['categories'])
    muscles = _normalize(plan_day['muscles'])
    profile_level_limit = PROFILE_LEVEL_LIMIT.get(profile.activity_level, 2)
    exercises = ExerciseLibrary.query.limit(1400).all()
    ranked = sorted(exercises, key=lambda item: _exercise_score(item, categories, muscles, profile_level_limit), reverse=True)
    selected = []
    seen_names = set()
    for exercise in ranked:
        if len(selected) >= limit:
            break
        if exercise.name.lower() in seen_names:
            continue
        if _exercise_score(exercise, categories, muscles, profile_level_limit) < 2.2:
            continue
        selected.append(exercise)
        seen_names.add(exercise.name.lower())
    return selected


def _prescribe_exercise(exercise, style, goal):
    scheme = STYLE_REP_SCHEMES.get(style, STYLE_REP_SCHEMES['mixed'])
    sets = scheme['sets']
    reps = scheme['reps']
    duration_seconds = scheme['duration_seconds']
    rest_seconds = scheme['rest_seconds']
    category = (exercise.category or '').lower()

    if category == 'cardio':
        duration_seconds = max(duration_seconds, 480 if goal == 'weight_loss' else 360)
        sets = 1
        reps = 0
        rest_seconds = 30 if goal == 'weight_loss' else 20
    elif category == 'stretching':
        duration_seconds = 50
        sets = 2
        reps = 0
        rest_seconds = 20
    elif goal == 'muscle_gain':
        sets = max(sets, 4)
        reps = 8 if reps == 0 else min(reps, 10)
        rest_seconds = max(rest_seconds, 75)
    elif goal == 'weight_loss':
        sets = max(sets, 3)
        reps = 15 if reps == 0 else max(reps, 12)
        rest_seconds = min(rest_seconds or 30, 45)

    estimated_duration_seconds = (duration_seconds * max(sets, 1)) + (rest_seconds * max(sets - 1, 0))
    estimated_calories_burn = round(max(20, estimated_duration_seconds / 60 * (8.5 if goal == 'weight_loss' else 6.5)), 1)
    instructions = exercise.instructions or []

    return {
        'exercise_id': exercise.external_id,
        'name': exercise.name,
        'sets': sets,
        'reps': reps,
        'duration_seconds': duration_seconds,
        'rest_seconds': rest_seconds,
        'duration_min': round(estimated_duration_seconds / 60),
        'estimated_duration_min': round(estimated_duration_seconds / 60),
        'estimated_calories_burn': estimated_calories_burn,
        'muscle_group': ', '.join((exercise.primary_muscles or [])[:2]) or exercise.category or 'full body',
        'description': instructions[0] if instructions else f'{exercise.name} for {exercise.category or "general fitness"}.',
        'instructions': instructions[:4],
        'exercise_tips': instructions[1:4] if len(instructions) > 1 else instructions[:1],
        'posture': instructions[0] if instructions else 'Move with control and neutral posture.',
        'posture_cues': instructions[1:3] if len(instructions) > 1 else ['Keep your core engaged.', 'Use smooth, controlled movement.'],
        'target_muscles': exercise.primary_muscles or [],
        'secondary_muscles': exercise.secondary_muscles or [],
        'equipments': [exercise.equipment] if exercise.equipment else [],
        'category': exercise.category,
        'level': exercise.level,
        'gif_url': None,
        'image_url': exercise.image_url,
        'video_url': None,
        'demo_media_url': exercise.demo_media_url or exercise.image_url,
        'has_demo_media': bool(exercise.image_url or exercise.demo_media_url),
        'media_fallback_text': instructions[0] if instructions else 'Follow the written cues for this movement.'
    }


def _build_rest_day(plan_day):
    return {
        'day': plan_day['day'],
        'plan_name': plan_day['title'],
        'theme': plan_day['title'],
        'is_rest_day': True,
        'total_duration_min': 20,
        'total_estimated_calories_burn': 60,
        'exercises': [{
            'name': plan_day['title'],
            'sets': 1,
            'reps': 0,
            'duration_seconds': 900,
            'rest_seconds': 0,
            'duration_min': 15,
            'estimated_duration_min': 15,
            'estimated_calories_burn': 60,
            'muscle_group': 'Recovery',
            'description': 'Light stretching, breathing work, or an easy walk to promote recovery.',
            'instructions': ['Spend 10-15 minutes on easy mobility work.', 'Keep intensity low and let recovery support tomorrow’s session.'],
            'exercise_tips': ['Focus on relaxed breathing.', 'Treat this as maintenance, not a skipped day.'],
            'posture': 'Relaxed recovery posture',
            'posture_cues': ['Move gently and avoid pain.', 'Keep breathing slow and even.'],
            'target_muscles': ['full body'],
            'secondary_muscles': [],
            'equipments': [],
            'category': 'recovery',
            'level': 'beginner',
            'gif_url': None,
            'image_url': None,
            'video_url': None,
            'demo_media_url': None,
            'has_demo_media': False,
            'media_fallback_text': 'Use this day for mobility and recovery work.'
        }]
    }


def generate_profile_workout_plan(profile):
    estimator = estimate_goal_timeline(profile)
    track = GOAL_TRACKS.get(profile.fitness_goal, GOAL_TRACKS['maintenance'])
    active_days_target = estimator['active_days_target']
    days = []

    for index, plan_day in enumerate(track):
        if index >= active_days_target and plan_day['day'] != 'Sun':
            days.append(_build_rest_day(plan_day))
            continue
        selected = _select_exercises(profile, plan_day, limit=4 if plan_day['style'] in {'recovery', 'mobility'} else 5)
        if not selected:
            days.append(_build_rest_day(plan_day))
            continue
        prescribed = [_prescribe_exercise(exercise, plan_day['style'], profile.fitness_goal) for exercise in selected]
        days.append({
            'day': plan_day['day'],
            'plan_name': f"{plan_day['day']} • {plan_day['title']}",
            'theme': plan_day['title'],
            'is_rest_day': False,
            'total_duration_min': sum(item['estimated_duration_min'] for item in prescribed),
            'total_estimated_calories_burn': round(sum(item['estimated_calories_burn'] for item in prescribed), 1),
            'exercises': prescribed
        })

    today_plan = next((day for day in days if day['day'] == _today_key()), None) or next((day for day in days if not day['is_rest_day']), days[0])
    hero_image_url = next((item.get('demo_media_url') for item in today_plan['exercises'] if item.get('demo_media_url')), HERO_IMAGES.get(profile.fitness_goal)) if today_plan else HERO_IMAGES.get(profile.fitness_goal)

    return {
        'status': 'success',
        'source': 'profile_ml',
        'goal': profile.fitness_goal,
        'bmi': float(profile.bmi or 0),
        'body_fat_percentage': float(getattr(profile, 'body_fat_percentage', 0) or 0),
        'body_fat_category': getattr(profile, 'body_fat_category', None),
        'goal_label': estimator['goal_label'],
        'goal_badge': estimator['goal_badge'],
        'hero_image_url': hero_image_url,
        'goal_eta_weeks': estimator['estimated_weeks'],
        'goal_confidence': estimator['confidence'],
        'plan_code': estimator['plan_code'],
        'plan_focus': estimator['focus'],
        'active_days_target': active_days_target,
        'target_weight_kg': estimator['target_weight_kg'],
        'target_bmi': estimator['target_bmi'],
        'target_body_fat_percentage': estimator['target_body_fat_percentage'],
        'reference_matches': estimator['reference_matches'],
        'model_summary': {
            'plan_code': estimator['plan_code'],
            'focus': estimator['focus'],
            'confidence': estimator['confidence'],
            'weekly_change_rate_kg': estimator['weekly_change_rate_kg'],
            'weight_delta_kg': estimator['weight_delta_kg'],
            'reference_matches': estimator['reference_matches']
        },
        'total_days': len(days),
        'active_days': sum(1 for day in days if not day['is_rest_day']),
        'total_duration_min': sum(day['total_duration_min'] for day in days),
        'total_estimated_calories_burn': round(sum(day['total_estimated_calories_burn'] for day in days), 1),
        'workout_stats': {
            'exercise_count': len(today_plan['exercises']) if today_plan else 0,
            'minutes': today_plan['total_duration_min'] if today_plan else 0,
            'calories': today_plan['total_estimated_calories_burn'] if today_plan else 0
        },
        'today_plan': today_plan,
        'days': days,
        'plan': days
    }
