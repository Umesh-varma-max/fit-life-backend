# models/doctor.py
from extensions import db
from datetime import datetime


class Doctor(db.Model):
    """Doctor listings for the doctor-help feature."""
    __tablename__ = 'doctors'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    specialization  = db.Column(db.String(150))
    hospital        = db.Column(db.String(200))
    contact_email   = db.Column(db.String(150))
    contact_phone   = db.Column(db.String(20))
    available_slots = db.Column(db.JSON)  # ["Mon 10am-1pm", "Wed 3pm-6pm"]
    rating          = db.Column(db.Numeric(3, 2), default=0.0)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':              self.id,
            'name':            self.name,
            'specialization':  self.specialization,
            'hospital':        self.hospital,
            'contact_email':   self.contact_email,
            'contact_phone':   self.contact_phone,
            'available_slots': self.available_slots or [],
            'rating':          float(self.rating) if self.rating else 0
        }
