# schemas/reminder_schema.py
from marshmallow import Schema, fields, validate


class ReminderSchema(Schema):
    """Validates reminder creation input."""
    reminder_type = fields.Str(required=True, validate=validate.OneOf(['workout', 'meal', 'water', 'sleep', 'custom']))
    message       = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    remind_at     = fields.Str(required=True)  # HH:MM format, parsed in controller
    repeat_daily  = fields.Bool(load_default=True)
