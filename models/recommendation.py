# models/recommendation.py
from extensions import db
from datetime import datetime


class Recommendation(db.Model):
    """AI-generated diet and workout recommendations for a user."""
    __tablename__ = 'recommendations'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    diet_plan      = db.Column(db.JSON)
    workout_plan   = db.Column(db.JSON)
    daily_calories = db.Column(db.Integer)
    weekly_tips    = db.Column(db.JSON)
    bmi_category   = db.Column(db.String(50))
    generated_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'bmi_category':   self.bmi_category,
            'daily_calories': self.daily_calories,
            'diet_plan':      self.diet_plan,
            'workout_plan':   self.workout_plan,
            'weekly_tips':    self.weekly_tips,
            'generated_at':   self.generated_at.isoformat() if self.generated_at else None
        }
