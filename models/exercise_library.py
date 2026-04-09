from datetime import datetime

from extensions import db


class ExerciseLibrary(db.Model):
    """Canonical exercise library imported from free-exercise-db."""

    __tablename__ = 'exercise_library'

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(160), nullable=False, index=True)
    slug = db.Column(db.String(180), nullable=False, index=True)
    source = db.Column(db.String(50), default='free-exercise-db', index=True)
    level = db.Column(db.String(50), index=True)
    category = db.Column(db.String(80), index=True)
    force = db.Column(db.String(50))
    mechanic = db.Column(db.String(50))
    equipment = db.Column(db.String(120), index=True)
    primary_muscles = db.Column(db.JSON, default=list)
    secondary_muscles = db.Column(db.JSON, default=list)
    instructions = db.Column(db.JSON, default=list)
    image_urls = db.Column(db.JSON, default=list)
    image_url = db.Column(db.String(500))
    demo_media_url = db.Column(db.String(500))
    tags = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'external_id': self.external_id,
            'name': self.name,
            'slug': self.slug,
            'source': self.source,
            'level': self.level,
            'category': self.category,
            'force': self.force,
            'mechanic': self.mechanic,
            'equipment': self.equipment,
            'primary_muscles': self.primary_muscles or [],
            'secondary_muscles': self.secondary_muscles or [],
            'instructions': self.instructions or [],
            'image_urls': self.image_urls or [],
            'image_url': self.image_url,
            'demo_media_url': self.demo_media_url,
            'tags': self.tags or []
        }
