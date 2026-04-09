# models/health_profile.py
from extensions import db
from datetime import datetime


class HealthProfile(db.Model):
    """Stores health metrics and fitness goals for a user."""
    __tablename__ = 'health_profiles'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    age            = db.Column(db.Integer, nullable=False)
    gender         = db.Column(db.Enum('male', 'female', 'other', name='gender_type'), nullable=False)
    height_cm      = db.Column(db.Numeric(5, 2), nullable=False)
    weight_kg      = db.Column(db.Numeric(5, 2), nullable=False)
    activity_level = db.Column(db.Enum('sedentary', 'light', 'moderate', 'active', name='activity_type'), nullable=False)
    sleep_hours    = db.Column(db.Numeric(4, 2), default=7.0)
    food_habits    = db.Column(db.Enum('veg', 'non-veg', 'vegan', 'keto', 'paleo', name='food_type'), default='non-veg')
    fitness_goal   = db.Column(db.Enum('weight_loss', 'muscle_gain', 'maintenance', name='goal_type'), nullable=False)
    bmi            = db.Column(db.Numeric(5, 2))
    body_fat_percentage = db.Column(db.Numeric(6, 2))
    body_fat_category = db.Column(db.String(50))
    bmr            = db.Column(db.Numeric(8, 2))
    daily_calories = db.Column(db.Integer)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'user_id':        self.user_id,
            'age':            self.age,
            'gender':         self.gender,
            'height_cm':      float(self.height_cm) if self.height_cm else None,
            'weight_kg':      float(self.weight_kg) if self.weight_kg else None,
            'activity_level': self.activity_level,
            'sleep_hours':    float(self.sleep_hours) if self.sleep_hours else 7.0,
            'food_habits':    self.food_habits,
            'fitness_goal':   self.fitness_goal,
            'bmi':            float(self.bmi) if self.bmi else None,
            'body_fat_percentage': float(self.body_fat_percentage) if self.body_fat_percentage else None,
            'body_fat_category': self.body_fat_category,
            'bmr':            float(self.bmr) if self.bmr else None,
            'daily_calories': self.daily_calories
        }
