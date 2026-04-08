from datetime import datetime

from extensions import db


class ExerciseLibrary(db.Model):
    """Structured exercise metadata imported from ExerciseDB-style datasets."""
    __tablename__ = 'exercise_library'

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    body_parts = db.Column(db.JSON, default=list)
    target_muscles = db.Column(db.JSON, default=list)
    secondary_muscles = db.Column(db.JSON, default=list)
    equipments = db.Column(db.JSON, default=list)
    keywords = db.Column(db.JSON, default=list)
    instructions = db.Column(db.JSON, default=list)
    exercise_tips = db.Column(db.JSON, default=list)
    variations = db.Column(db.JSON, default=list)
    related_exercise_ids = db.Column(db.JSON, default=list)
    gender = db.Column(db.String(20))
    exercise_type = db.Column(db.String(50))
    overview = db.Column(db.Text)
    image_url = db.Column(db.Text)
    gif_url = db.Column(db.Text)
    video_url = db.Column(db.Text)
    source = db.Column(db.String(50), default='ExerciseDB')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'external_id': self.external_id,
            'name': self.name,
            'body_parts': self.body_parts or [],
            'target_muscles': self.target_muscles or [],
            'secondary_muscles': self.secondary_muscles or [],
            'equipments': self.equipments or [],
            'keywords': self.keywords or [],
            'instructions': self.instructions or [],
            'exercise_tips': self.exercise_tips or [],
            'variations': self.variations or [],
            'related_exercise_ids': self.related_exercise_ids or [],
            'gender': self.gender,
            'exercise_type': self.exercise_type,
            'overview': self.overview,
            'image_url': self.image_url,
            'gif_url': self.gif_url,
            'video_url': self.video_url,
            'source': self.source
        }
