# utils/bmi_calculator.py
"""
BMI, BMR, TDEE, and daily calorie calculations.
Uses the Mifflin-St Jeor equation — most accurate for most people.
"""

ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light':     1.375,
    'moderate':  1.55,
    'active':    1.725
}

GOAL_CALORIE_ADJUSTMENTS = {
    'weight_loss':  -500,   # calorie deficit
    'muscle_gain':  +300,   # calorie surplus
    'maintenance':     0    # no adjustment
}


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """BMI = weight(kg) / height(m)^2"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def get_bmi_category(bmi: float) -> str:
    """Returns human-readable BMI category."""
    if bmi < 18.5:
        return 'Underweight'
    if bmi < 25.0:
        return 'Normal'
    if bmi < 30.0:
        return 'Overweight'
    return 'Obese'


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor Equation.
    Male:   BMR = (10 × weight) + (6.25 × height) − (5 × age) + 5
    Female: BMR = (10 × weight) + (6.25 × height) − (5 × age) − 161
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender == 'male':
        return round(base + 5, 2)
    else:
        return round(base - 161, 2)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Total Daily Energy Expenditure = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier, 2)


def calculate_daily_calories(tdee: float, goal: str) -> int:
    """Adjust TDEE based on fitness goal. Never below 1200 kcal."""
    adjustment = GOAL_CALORIE_ADJUSTMENTS.get(goal, 0)
    return max(1200, int(tdee + adjustment))
