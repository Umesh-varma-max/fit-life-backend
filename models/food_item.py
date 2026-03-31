# models/food_item.py
from extensions import db


class FoodItem(db.Model):
    """Food nutrition database — searchable by name or barcode."""
    __tablename__ = 'food_items'

    id                = db.Column(db.Integer, primary_key=True)
    name              = db.Column(db.String(150), nullable=False, index=True)
    calories_per_100g = db.Column(db.Numeric(7, 2))
    protein_g         = db.Column(db.Numeric(6, 2))
    carbs_g           = db.Column(db.Numeric(6, 2))
    fat_g             = db.Column(db.Numeric(6, 2))
    fiber_g           = db.Column(db.Numeric(6, 2))
    barcode           = db.Column(db.String(50), index=True)
    source            = db.Column(db.String(50), default='manual')

    def to_dict(self):
        return {
            'id':                self.id,
            'name':              self.name,
            'calories_per_100g': float(self.calories_per_100g) if self.calories_per_100g else 0,
            'protein_g':         float(self.protein_g) if self.protein_g else 0,
            'carbs_g':           float(self.carbs_g) if self.carbs_g else 0,
            'fat_g':             float(self.fat_g) if self.fat_g else 0,
            'fiber_g':           float(self.fiber_g) if self.fiber_g else 0
        }
