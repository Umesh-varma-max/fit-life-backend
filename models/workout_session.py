from datetime import datetime

from extensions import db


class WorkoutSession(db.Model):
    """Tracks an in-progress or completed workout session for timer-based frontend flows."""
    __tablename__ = 'workout_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    day_of_week = db.Column(db.Enum('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', name='workout_session_day_enum'))
    goal_label = db.Column(db.String(80))
    goal_key = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active', nullable=False, index=True)
    current_exercise_index = db.Column(db.Integer, default=0, nullable=False)
    exercises = db.Column(db.JSON, default=list)
    completed_exercises = db.Column(db.JSON, default=list)
    total_duration_seconds = db.Column(db.Integer, default=0)
    total_calories_burned = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        exercises = self.exercises or []
        completed = self.completed_exercises or []
        current = None
        if 0 <= self.current_exercise_index < len(exercises):
            current = exercises[self.current_exercise_index]

        return {
            'id': self.id,
            'day': self.day_of_week,
            'goal_label': self.goal_label,
            'goal_key': self.goal_key,
            'status': self.status,
            'current_exercise_index': self.current_exercise_index,
            'current_exercise': current,
            'completed_exercises': completed,
            'exercises': exercises,
            'total_duration_seconds': self.total_duration_seconds,
            'total_calories_burned': self.total_calories_burned,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
