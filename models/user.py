# models/user.py
from extensions import db
from datetime import datetime


class User(db.Model):
    """Represents an authenticated user account."""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.Enum('user', 'admin', name='user_role'), default='user')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile         = db.relationship('HealthProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    activity_logs   = db.relationship('ActivityLog', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    recommendations = db.relationship('Recommendation', backref='user', cascade='all, delete-orphan')
    workout_plans   = db.relationship('WorkoutPlan', backref='user', cascade='all, delete-orphan')
    workout_sessions = db.relationship('WorkoutSession', backref='user', cascade='all, delete-orphan')
    reminders       = db.relationship('Reminder', backref='user', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':         self.id,
            'full_name':  self.full_name,
            'email':      self.email,
            'role':       self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
