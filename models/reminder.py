# models/reminder.py
from extensions import db
from datetime import datetime


class Reminder(db.Model):
    """User reminders for workouts, meals, water, sleep, or custom alerts."""
    __tablename__ = 'reminders'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    reminder_type = db.Column(db.Enum('workout', 'meal', 'water', 'sleep', 'custom', name='reminder_type_enum'), nullable=False)
    message       = db.Column(db.Text)
    remind_at     = db.Column(db.Time)
    repeat_daily  = db.Column(db.Boolean, default=True)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':            self.id,
            'reminder_type': self.reminder_type,
            'message':       self.message,
            'remind_at':     str(self.remind_at) if self.remind_at else None,
            'repeat_daily':  self.repeat_daily,
            'is_active':     self.is_active
        }
