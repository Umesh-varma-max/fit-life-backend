# models/activity_log.py
from extensions import db
from datetime import datetime, date


class ActivityLog(db.Model):
    """One log entry: meal, workout, water, or sleep."""
    __tablename__ = 'activity_logs'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    log_date     = db.Column(db.Date, nullable=False, default=date.today, index=True)
    log_type     = db.Column(db.Enum('meal', 'workout', 'water', 'sleep', name='log_type_enum'), nullable=False)
    description  = db.Column(db.String(255))
    calories_in  = db.Column(db.Integer, default=0)
    calories_out = db.Column(db.Integer, default=0)
    water_ml     = db.Column(db.Integer, default=0)
    sleep_hours  = db.Column(db.Numeric(4, 2), default=0)
    duration_min = db.Column(db.Integer, default=0)
    details      = db.Column(db.JSON)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite index for efficient date-based queries
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'log_date'),
    )

    def to_dict(self):
        return {
            'id':           self.id,
            'log_type':     self.log_type,
            'description':  self.description,
            'calories_in':  self.calories_in,
            'calories_out': self.calories_out,
            'water_ml':     self.water_ml,
            'sleep_hours':  float(self.sleep_hours) if self.sleep_hours else 0,
            'duration_min': self.duration_min,
            'details':      self.details or {},
            'log_date':     str(self.log_date),
            'created_at':   self.created_at.isoformat() if self.created_at else None
        }
