# models/workout_plan.py
from extensions import db
from datetime import datetime


class WorkoutPlan(db.Model):
    """User's custom workout plan for a specific day of the week."""
    __tablename__ = 'workout_plans'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    plan_name   = db.Column(db.String(100))
    day_of_week = db.Column(db.Enum('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', name='day_enum'))
    exercises   = db.Column(db.JSON)  # [{name, sets, reps, duration_min}]
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':        self.id,
            'plan_name': self.plan_name,
            'day':       self.day_of_week,
            'exercises': self.exercises or []
        }
