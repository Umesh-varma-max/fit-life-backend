from datetime import datetime

from extensions import db


class BodyMetricReference(db.Model):
    """Reference records used by the goal estimator to approximate timelines."""

    __tablename__ = 'body_metric_references'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(40), nullable=False, index=True)
    gender = db.Column(db.String(20), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False, index=True)
    height_m = db.Column(db.Numeric(6, 4), nullable=False)
    weight_kg = db.Column(db.Numeric(7, 3), nullable=False)
    bmi = db.Column(db.Numeric(6, 3), nullable=False, index=True)
    bmi_case = db.Column(db.String(50), index=True)
    body_fat_percentage = db.Column(db.Numeric(6, 3))
    body_fat_case = db.Column(db.String(50), index=True)
    recommendation_plan = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'gender': self.gender,
            'age': self.age,
            'height_m': float(self.height_m) if self.height_m is not None else None,
            'weight_kg': float(self.weight_kg) if self.weight_kg is not None else None,
            'bmi': float(self.bmi) if self.bmi is not None else None,
            'bmi_case': self.bmi_case,
            'body_fat_percentage': float(self.body_fat_percentage) if self.body_fat_percentage is not None else None,
            'body_fat_case': self.body_fat_case,
            'recommendation_plan': self.recommendation_plan
        }
