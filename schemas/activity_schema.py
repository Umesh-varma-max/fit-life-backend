# schemas/activity_schema.py
from marshmallow import Schema, fields, validate


class ActivityLogSchema(Schema):
    """Validates activity log entries (meal, workout, water, sleep)."""
    log_type     = fields.Str(required=True, validate=validate.OneOf(['meal', 'workout', 'water', 'sleep']))
    description  = fields.Str(load_default=None)
    calories_in  = fields.Int(load_default=0, validate=validate.Range(min=0))
    calories_out = fields.Int(load_default=0, validate=validate.Range(min=0))
    water_ml     = fields.Int(load_default=0, validate=validate.Range(min=0))
    sleep_hours  = fields.Float(load_default=0.0)
    duration_min = fields.Int(load_default=0)
    log_date     = fields.Date(load_default=None)  # defaults to today if omitted
