from datetime import datetime

from extensions import db


class BodyMetricReference(db.Model):
    """Reference rows imported from BMI/BFP datasets to guide workout intensity."""
    __tablename__ = 'body_metric_references'

    id = db.Column(db.Integer, primary_key=True)
    source_dataset = db.Column(db.String(20), nullable=False, index=True)
    weight = db.Column(db.Numeric(7, 3))
    height = db.Column(db.Numeric(7, 3))
    bmi = db.Column(db.Numeric(6, 3), index=True)
    body_fat_percentage = db.Column(db.Numeric(6, 3), nullable=True, index=True)
    category = db.Column(db.String(50))
    gender = db.Column(db.String(20), index=True)
    age = db.Column(db.Integer, index=True)
    bmi_case = db.Column(db.String(50))
    exercise_recommendation_plan = db.Column(db.Integer, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'source_dataset': self.source_dataset,
            'weight': float(self.weight) if self.weight is not None else None,
            'height': float(self.height) if self.height is not None else None,
            'bmi': float(self.bmi) if self.bmi is not None else None,
            'body_fat_percentage': float(self.body_fat_percentage) if self.body_fat_percentage is not None else None,
            'category': self.category,
            'gender': self.gender,
            'age': self.age,
            'bmi_case': self.bmi_case,
            'exercise_recommendation_plan': self.exercise_recommendation_plan
        }
