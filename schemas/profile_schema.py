# schemas/profile_schema.py
from marshmallow import Schema, fields, validate, pre_load


GOAL_ALIASES = {
    'get fitter': 'maintenance',
    'gain weight': 'muscle_gain',
    'lose weight': 'weight_loss',
    'building muscles': 'muscle_gain',
    'improving endurance': 'maintenance',
    'others': 'maintenance',
    'maintenance': 'maintenance',
    'muscle gain': 'muscle_gain',
    'weight loss': 'weight_loss',
    'muscle_gain': 'muscle_gain',
    'weight_loss': 'weight_loss'
}

ACTIVITY_ALIASES = {
    'beginner': 'light',
    'intermediate': 'moderate',
    'advanced': 'active',
    'sedentary': 'sedentary',
    'light': 'light',
    'moderate': 'moderate',
    'active': 'active'
}

GENDER_ALIASES = {
    'male': 'male',
    'female': 'female',
    'other': 'other'
}


class HealthProfileSchema(Schema):
    """Validates health profile creation/update input."""
    age            = fields.Int(required=True, validate=validate.Range(min=10, max=120))
    gender         = fields.Str(required=True, validate=validate.OneOf(['male', 'female', 'other']))
    height_cm      = fields.Float(required=True, validate=validate.Range(min=50, max=280))
    weight_kg      = fields.Float(required=True, validate=validate.Range(min=10, max=500))
    activity_level = fields.Str(required=True, validate=validate.OneOf(['sedentary', 'light', 'moderate', 'active']))
    sleep_hours    = fields.Float(load_default=7.0, validate=validate.Range(min=0, max=24))
    food_habits    = fields.Str(load_default='non-veg', validate=validate.OneOf(['veg', 'non-veg', 'vegan', 'keto', 'paleo']))
    fitness_goal   = fields.Str(required=True, validate=validate.OneOf(['weight_loss', 'muscle_gain', 'maintenance']))

    @pre_load
    def normalize_onboarding_payload(self, data, **kwargs):
        """Accept mobile onboarding labels and height units from the frontend."""
        if not isinstance(data, dict):
            return data

        normalized = dict(data)

        gender = str(normalized.get('gender', '')).strip().lower()
        if gender in GENDER_ALIASES:
            normalized['gender'] = GENDER_ALIASES[gender]

        activity_level = str(normalized.get('activity_level', normalized.get('activity', ''))).strip().lower()
        if activity_level in ACTIVITY_ALIASES:
            normalized['activity_level'] = ACTIVITY_ALIASES[activity_level]

        goal = str(normalized.get('fitness_goal', normalized.get('goal', ''))).strip().lower()
        if goal in GOAL_ALIASES:
            normalized['fitness_goal'] = GOAL_ALIASES[goal]

        height_unit = str(normalized.get('height_unit', 'cm')).strip().lower()
        if 'height_cm' not in normalized:
            if height_unit == 'ft':
                feet = float(normalized.get('height_ft', normalized.get('height', 0)) or 0)
                inches = float(normalized.get('height_in', 0) or 0)
                total_inches = (feet * 12) + inches
                if total_inches > 0:
                    normalized['height_cm'] = round(total_inches * 2.54, 2)
            else:
                height_value = normalized.get('height', normalized.get('height_value'))
                if height_value not in (None, ''):
                    normalized['height_cm'] = height_value

        weight_value = normalized.get('weight', normalized.get('weight_value'))
        if 'weight_kg' not in normalized and weight_value not in (None, ''):
            normalized['weight_kg'] = weight_value

        return normalized
