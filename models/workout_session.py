from datetime import datetime

from extensions import db


class WorkoutSession(db.Model):
    """Tracks timer-driven workout execution for the advanced workout flow."""

    __tablename__ = 'workout_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='active', index=True)
    day = db.Column(db.String(10), nullable=False)
    goal = db.Column(db.String(50))
    session_title = db.Column(db.String(160))
    plan_snapshot = db.Column(db.JSON, nullable=False)
    current_exercise_index = db.Column(db.Integer, default=0)
    completed_exercises = db.Column(db.JSON, default=list)
    total_duration_seconds = db.Column(db.Integer, default=0)
    total_calories_burned = db.Column(db.Numeric(8, 2), default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        exercises = (self.plan_snapshot or {}).get('exercises', [])
        current_index = min(self.current_exercise_index or 0, max(len(exercises) - 1, 0))
        current_exercise = exercises[current_index] if exercises else None

        return {
            'id': self.id,
            'status': self.status,
            'day': self.day,
            'goal': self.goal,
            'session_title': self.session_title,
            'current_exercise_index': self.current_exercise_index or 0,
            'current_exercise': current_exercise,
            'completed_exercises': self.completed_exercises or [],
            'total_duration_seconds': self.total_duration_seconds or 0,
            'total_calories_burned': float(self.total_calories_burned or 0),
            'plan_snapshot': self.plan_snapshot or {},
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
