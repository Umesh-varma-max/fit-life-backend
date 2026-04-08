from datetime import datetime

from extensions import db


class WorkoutSession(db.Model):
    """Tracks an in-progress or completed workout session for timer-driven flows."""
    __tablename__ = 'workout_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    goal = db.Column(db.String(50))
    day_of_week = db.Column(db.String(10))
    session_name = db.Column(db.String(150))
    status = db.Column(db.String(20), default='active', index=True)
    current_exercise_index = db.Column(db.Integer, default=0)
    plan_snapshot = db.Column(db.JSON, default=list)
    completed_exercises = db.Column(db.JSON, default=list)
    total_duration_seconds = db.Column(db.Integer, default=0)
    total_calories_burned = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'goal': self.goal,
            'day_of_week': self.day_of_week,
            'session_name': self.session_name,
            'status': self.status,
            'current_exercise_index': self.current_exercise_index,
            'plan_snapshot': self.plan_snapshot or [],
            'completed_exercises': self.completed_exercises or [],
            'total_duration_seconds': self.total_duration_seconds or 0,
            'total_calories_burned': self.total_calories_burned or 0,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
