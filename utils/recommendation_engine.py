# utils/recommendation_engine.py
"""
Rule-based recommendation engine.
Selects diet template + workout template + weekly tips based on
BMI, fitness goal, and food preference.
"""

from utils.bmi_calculator import get_bmi_category
from utils.diet_templates import DIET_TEMPLATES
from utils.workout_templates import build_goal_based_workout_plan

WEEKLY_TIPS = {
    'weight_loss': [
        "Drink 3L water daily — it boosts metabolism.",
        "Walk 10,000 steps per day as a baseline.",
        "Avoid processed sugars and trans fats.",
        "Track every meal — awareness reduces overeating.",
        "Sleep 7-8 hours — poor sleep increases hunger hormones."
    ],
    'muscle_gain': [
        "Eat 1.6-2.2g protein per kg of body weight.",
        "Progressive overload: increase weight each week.",
        "Rest muscles 48 hours between same-group sessions.",
        "Creatine monohydrate is the most evidence-backed supplement.",
        "Prioritize compound lifts: squat, deadlift, bench press."
    ],
    'maintenance': [
        "Consistency beats perfection — stick to your routine.",
        "Maintain your calorie balance — log weekly, not daily.",
        "Mix cardio and strength to preserve both fitness types.",
        "Stay hydrated — 2.5-3L daily.",
        "Schedule one active recovery day per week."
    ]
}


def generate_recommendation(profile) -> dict:
    """
    Rule-based engine.
    Takes a HealthProfile object, returns recommendation dict.
    """
    bmi       = float(profile.bmi) if profile.bmi is not None else None
    goal      = profile.fitness_goal
    food_pref = profile.food_habits
    daily_cal = profile.daily_calories

    bmi_cat = get_bmi_category(bmi) if bmi is not None else 'Unknown'

    # Select diet and workout template keys based on goal + BMI
    if goal == 'muscle_gain' or (bmi is not None and bmi < 18.5):
        diet_key    = 'high_protein'
        workout_key = 'strength'
    elif goal == 'weight_loss' or (bmi is not None and bmi >= 25):
        diet_key    = 'low_cal'
        workout_key = 'cardio'
    else:
        diet_key    = 'balanced'
        workout_key = 'mixed'

    # Food preference fallback: use 'non-veg' if preference not in template
    food_key = food_pref if food_pref in DIET_TEMPLATES[diet_key] else 'non-veg'

    diet_plan = DIET_TEMPLATES[diet_key][food_key]
    workout_plan_details = build_goal_based_workout_plan(goal)
    workout_plan = {
        day['day']: [
            {
                'name': exercise.get('name'),
                'sets': exercise.get('sets', 0),
                'reps': exercise.get('reps', 0),
                'duration_min': exercise.get('estimated_duration_min') or exercise.get('duration_min', 0)
            }
            for exercise in day.get('exercises', [])
        ]
        for day in workout_plan_details.get('days', [])
    }
    tips         = WEEKLY_TIPS.get(goal, WEEKLY_TIPS['maintenance'])

    return {
        'bmi_category':   bmi_cat,
        'daily_calories': daily_cal,
        'diet_plan':      diet_plan,
        'workout_plan':   workout_plan,
        'weekly_tips':    tips
    }
