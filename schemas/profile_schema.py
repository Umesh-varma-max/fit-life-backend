# schemas/profile_schema.py
from marshmallow import Schema, fields, validate


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
