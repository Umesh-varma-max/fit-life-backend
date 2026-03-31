# models/trainer.py
from extensions import db
from datetime import datetime


class Trainer(db.Model):
    """Fitness trainer listings for the trainer-connect feature."""
    __tablename__ = 'trainers'

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(150))
    location       = db.Column(db.String(200))
    contact_email  = db.Column(db.String(150))
    contact_phone  = db.Column(db.String(20))
    rating         = db.Column(db.Numeric(3, 2), default=0.0)
    available      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'name':           self.name,
            'specialization': self.specialization,
            'location':       self.location,
            'contact_email':  self.contact_email,
            'contact_phone':  self.contact_phone,
            'rating':         float(self.rating) if self.rating else 0,
            'available':      self.available
        }
