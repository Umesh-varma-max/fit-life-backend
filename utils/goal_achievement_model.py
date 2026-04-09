"""A lightweight model-backed estimator for fitness goal timelines."""

from __future__ import annotations

from statistics import mean

from models.body_metric_reference import BodyMetricReference


PLAN_CODE_FOCUS = {
    1: 'mobility_reset',
    2: 'foundation_strength',
    3: 'balanced_recomposition',
    4: 'conditioning_plus_strength',
    5: 'accelerated_fat_loss',
    6: 'high_volume_transformation'
}

GOAL_BADGES = {
    'weight_loss': 'LOSE WEIGHT',
    'muscle_gain': 'BUILD MUSCLE',
    'maintenance': 'STAY FIT'
}

GOAL_LABELS = {
    'weight_loss': 'Adaptive Fat-Loss Plan',
    'muscle_gain': 'Lean Muscle Blueprint',
    'maintenance': 'Performance Balance Plan'
}


def _activity_day_target(activity_level: str) -> int:
    return {
        'sedentary': 3,
        'light': 4,
        'moderate': 5,
        'active': 6
    }.get(activity_level, 4)


def _goal_target_bmi(goal: str, gender: str) -> float:
    if goal == 'weight_loss':
        return 22.5 if gender == 'female' else 23.0
    if goal == 'muscle_gain':
        return 23.5 if gender == 'female' else 24.5
    return 22.8 if gender == 'female' else 23.5


def _target_body_fat(goal: str, gender: str) -> float:
    if gender == 'female':
        return {'weight_loss': 24.0, 'muscle_gain': 25.0}.get(goal, 27.0)
    return {'weight_loss': 16.0, 'muscle_gain': 15.0}.get(goal, 18.0)


def _safe_weekly_change(goal: str) -> float:
    return {
        'weight_loss': 0.65,
        'muscle_gain': 0.28,
        'maintenance': 0.18
    }.get(goal, 0.2)


def _candidate_distance(profile, record) -> float:
    bmi_delta = abs(float(record.bmi) - float(profile.bmi or 0))
    age_delta = abs(int(record.age) - int(profile.age))
    bfp_delta = 0.0
    if getattr(profile, 'body_fat_percentage', None) is not None and record.body_fat_percentage is not None:
        bfp_delta = abs(float(record.body_fat_percentage) - float(profile.body_fat_percentage))
    return (bmi_delta * 2.4) + (age_delta * 0.12) + (bfp_delta * 1.6)


def _reference_matches(profile):
    query = BodyMetricReference.query.filter_by(gender=str(profile.gender).title())
    candidates = list(query.limit(1200))
    if not candidates:
        return []
    ranked = sorted(candidates, key=lambda row: _candidate_distance(profile, row))
    return ranked[:12]


def estimate_goal_timeline(profile) -> dict:
    """Estimate time-to-goal and a recommended workout intensity band."""
    weight_kg = float(profile.weight_kg or 0)
    height_m = float(profile.height_cm or 0) / 100.0 if profile.height_cm else 0
    active_days = _activity_day_target(profile.activity_level)
    target_bmi = _goal_target_bmi(profile.fitness_goal, profile.gender)
    target_weight = round(target_bmi * (height_m ** 2), 1) if height_m else weight_kg
    raw_change = round(target_weight - weight_kg, 1)
    weekly_rate = _safe_weekly_change(profile.fitness_goal)

    if profile.fitness_goal == 'weight_loss':
        delta_kg = max(0.0, weight_kg - target_weight)
    elif profile.fitness_goal == 'muscle_gain':
        delta_kg = max(0.0, target_weight - weight_kg)
    else:
        delta_kg = max(1.5, abs(raw_change))

    heuristic_weeks = max(4, round(delta_kg / weekly_rate)) if weekly_rate else 8

    matches = _reference_matches(profile)
    plan_code = None
    if matches:
        plan_code = round(mean(match.recommendation_plan for match in matches))

    if plan_code is None:
        if profile.fitness_goal == 'weight_loss':
            plan_code = 5 if float(profile.bmi or 0) >= 30 else 4
        elif profile.fitness_goal == 'muscle_gain':
            plan_code = 3 if float(profile.bmi or 0) < 21 else 4
        else:
            plan_code = 3

    if matches:
        ref_weeks = []
        for match in matches:
            match_gap = abs(float(match.bmi) - target_bmi)
            ref_weeks.append(max(4, round((match_gap * 1.8) + (match.recommendation_plan * 1.6))))
        estimated_weeks = round((heuristic_weeks * 0.55) + (mean(ref_weeks) * 0.45))
        confidence = 'high'
    else:
        estimated_weeks = heuristic_weeks
        confidence = 'medium'

    focus = PLAN_CODE_FOCUS.get(int(plan_code), 'balanced_recomposition')
    target_body_fat = _target_body_fat(profile.fitness_goal, profile.gender)
    current_bfp = float(getattr(profile, 'body_fat_percentage', 0) or 0)
    body_fat_gap = max(0.0, current_bfp - target_body_fat) if profile.fitness_goal == 'weight_loss' else abs(current_bfp - target_body_fat)

    return {
        'goal_label': GOAL_LABELS.get(profile.fitness_goal, 'Adaptive Fitness Plan'),
        'goal_badge': GOAL_BADGES.get(profile.fitness_goal, 'FITNESS'),
        'focus': focus,
        'plan_code': int(plan_code),
        'active_days_target': active_days,
        'target_weight_kg': target_weight,
        'target_bmi': round(target_bmi, 2),
        'target_body_fat_percentage': round(target_body_fat, 1),
        'body_fat_gap': round(body_fat_gap, 1),
        'estimated_weeks': int(max(4, estimated_weeks)),
        'confidence': confidence,
        'weekly_change_rate_kg': weekly_rate,
        'weight_delta_kg': round(delta_kg, 1),
        'reference_matches': len(matches)
    }
