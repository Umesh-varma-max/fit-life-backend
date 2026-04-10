# models/activity_log.py
from flask import current_app, has_app_context, has_request_context, url_for

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
    image_blob   = db.Column(db.LargeBinary)
    image_mime_type = db.Column(db.String(100))
    image_filename = db.Column(db.String(255))
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Composite index for efficient date-based queries
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'log_date'),
    )

    def to_dict(self):
        image_url = None
        if self.image_blob and has_app_context():
            if has_request_context():
                image_url = url_for('activity.activity_image_get', log_id=self.id, _external=True)
            else:
                base_url = (current_app.config.get('API_BASE_URL') or '').rstrip('/')
                image_url = f"{base_url}/api/activity/{self.id}/image" if base_url else f"/api/activity/{self.id}/image"

        return {
            'id':           self.id,
            'log_type':     self.log_type,
            'description':  self.description,
            'calories_in':  self.calories_in,
            'calories_out': self.calories_out,
            'water_ml':     self.water_ml,
            'sleep_hours':  float(self.sleep_hours) if self.sleep_hours else 0,
            'duration_min': self.duration_min,
            'image_url':    image_url,
            'thumbnail_url': image_url,
            'has_image':    bool(self.image_blob),
            'log_date':     str(self.log_date),
            'created_at':   self.created_at.isoformat() if self.created_at else None
        }
