"""Body-fat estimation helpers used for profile-aware workout planning."""


def estimate_body_fat_percentage(bmi: float, age: int, gender: str) -> float:
    """Estimate body fat percentage using the Deurenberg-style formula."""
    sex_flag = 1.0 if gender == 'male' else 0.0 if gender == 'female' else 0.5
    estimated = (1.20 * bmi) + (0.23 * age) - (10.8 * sex_flag) - 5.4
    return round(max(5.0, min(estimated, 60.0)), 2)


def body_fat_category(body_fat_percentage: float, gender: str) -> str:
    """Classify estimated body fat using practical fitness ranges."""
    if gender == 'male':
        if body_fat_percentage < 6:
            return 'Essential'
        if body_fat_percentage < 14:
            return 'Athletes'
        if body_fat_percentage < 18:
            return 'Fitness'
        if body_fat_percentage < 25:
            return 'Acceptable'
        return 'Obese'

    if gender == 'female':
        if body_fat_percentage < 14:
            return 'Essential'
        if body_fat_percentage < 21:
            return 'Athletes'
        if body_fat_percentage < 25:
            return 'Fitness'
        if body_fat_percentage < 32:
            return 'Acceptable'
        return 'Obese'

    if body_fat_percentage < 10:
        return 'Essential'
    if body_fat_percentage < 20:
        return 'Athletes'
    if body_fat_percentage < 26:
        return 'Fitness'
    if body_fat_percentage < 30:
        return 'Acceptable'
    return 'Obese'
