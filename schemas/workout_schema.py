# schemas/workout_schema.py
from marshmallow import Schema, fields, validate


class ExerciseSchema(Schema):
    """Validates individual exercise entries within a workout plan."""
    name                     = fields.Str(required=True)
    sets                     = fields.Int(load_default=0, validate=validate.Range(min=0))
    reps                     = fields.Int(load_default=0, validate=validate.Range(min=0))
    duration_min             = fields.Int(load_default=0, validate=validate.Range(min=0))
    duration_seconds         = fields.Int(load_default=0, validate=validate.Range(min=0))
    rest_seconds             = fields.Int(load_default=0, validate=validate.Range(min=0))
    muscle_group             = fields.Str(load_default=None, allow_none=True)
    description              = fields.Str(load_default=None, allow_none=True)
    posture                  = fields.Str(load_default=None, allow_none=True)
    posture_cues             = fields.List(fields.Str(), load_default=list)
    instructions             = fields.List(fields.Str(), load_default=list)
    exercise_tips            = fields.List(fields.Str(), load_default=list)
    body_parts               = fields.List(fields.Str(), load_default=list)
    target_muscles           = fields.List(fields.Str(), load_default=list)
    secondary_muscles        = fields.List(fields.Str(), load_default=list)
    equipments               = fields.List(fields.Str(), load_default=list)
    gif_url                  = fields.Str(load_default=None, allow_none=True)
    image_url                = fields.Str(load_default=None, allow_none=True)
    video_url                = fields.Str(load_default=None, allow_none=True)
    demo_media_url           = fields.Str(load_default=None, allow_none=True)
    estimated_duration_min   = fields.Int(load_default=0, validate=validate.Range(min=0))
    estimated_calories_burn  = fields.Int(load_default=0, validate=validate.Range(min=0))


class WorkoutPlanSchema(Schema):
    """Validates workout plan for a specific day."""
    day       = fields.Str(required=True, validate=validate.OneOf(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']))
    plan_name = fields.Str(load_default=None)
    exercises = fields.List(fields.Nested(ExerciseSchema), required=True)
