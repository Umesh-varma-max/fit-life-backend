# seed_food_data.py
"""
Seed script: Populate the food_items table with common Indian and international foods.
Run: python seed_food_data.py
"""

from app import create_app
from extensions import db
from models.food_item import FoodItem

FOOD_DATA = [
    # ─── Indian Foods ─────────────────────────────────────
    {"name": "Chapati / Roti", "calories_per_100g": 297, "protein_g": 8.7, "carbs_g": 56.0, "fat_g": 3.7, "fiber_g": 2.7, "source": "seed"},
    {"name": "Basmati Rice (Cooked)", "calories_per_100g": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3, "fiber_g": 0.4, "source": "seed"},
    {"name": "Brown Rice (Cooked)", "calories_per_100g": 112, "protein_g": 2.6, "carbs_g": 23.5, "fat_g": 0.9, "fiber_g": 1.8, "source": "seed"},
    {"name": "Dal (Toor / Arhar)", "calories_per_100g": 198, "protein_g": 22.0, "carbs_g": 36.0, "fat_g": 1.2, "fiber_g": 8.0, "source": "seed"},
    {"name": "Moong Dal", "calories_per_100g": 105, "protein_g": 7.0, "carbs_g": 18.0, "fat_g": 0.4, "fiber_g": 6.0, "source": "seed"},
    {"name": "Rajma (Kidney Beans)", "calories_per_100g": 127, "protein_g": 8.7, "carbs_g": 22.8, "fat_g": 0.5, "fiber_g": 6.4, "source": "seed"},
    {"name": "Chole / Chickpeas", "calories_per_100g": 164, "protein_g": 8.9, "carbs_g": 27.4, "fat_g": 2.6, "fiber_g": 7.6, "source": "seed"},
    {"name": "Paneer", "calories_per_100g": 265, "protein_g": 18.3, "carbs_g": 1.2, "fat_g": 20.8, "fiber_g": 0.0, "source": "seed"},
    {"name": "Curd / Yogurt", "calories_per_100g": 61, "protein_g": 3.5, "carbs_g": 4.7, "fat_g": 3.3, "fiber_g": 0.0, "source": "seed"},
    {"name": "Idli (1 piece ~30g)", "calories_per_100g": 39, "protein_g": 2.0, "carbs_g": 8.0, "fat_g": 0.1, "fiber_g": 0.9, "source": "seed"},
    {"name": "Dosa (Plain)", "calories_per_100g": 168, "protein_g": 3.9, "carbs_g": 28.0, "fat_g": 4.0, "fiber_g": 1.2, "source": "seed"},
    {"name": "Upma", "calories_per_100g": 132, "protein_g": 3.5, "carbs_g": 18.0, "fat_g": 5.0, "fiber_g": 1.5, "source": "seed"},
    {"name": "Poha (Flattened Rice)", "calories_per_100g": 130, "protein_g": 2.5, "carbs_g": 26.0, "fat_g": 2.0, "fiber_g": 1.0, "source": "seed"},
    {"name": "Sambar", "calories_per_100g": 65, "protein_g": 3.0, "carbs_g": 9.0, "fat_g": 2.0, "fiber_g": 2.5, "source": "seed"},
    {"name": "Palak Paneer", "calories_per_100g": 120, "protein_g": 7.0, "carbs_g": 5.0, "fat_g": 8.5, "fiber_g": 2.0, "source": "seed"},
    {"name": "Butter Chicken", "calories_per_100g": 148, "protein_g": 12.0, "carbs_g": 5.0, "fat_g": 9.0, "fiber_g": 0.5, "source": "seed"},
    {"name": "Biryani (Chicken)", "calories_per_100g": 175, "protein_g": 8.5, "carbs_g": 22.0, "fat_g": 6.0, "fiber_g": 1.0, "source": "seed"},

    # ─── Fruits ───────────────────────────────────────────
    {"name": "Banana", "calories_per_100g": 89, "protein_g": 1.1, "carbs_g": 22.8, "fat_g": 0.3, "fiber_g": 2.6, "source": "seed"},
    {"name": "Apple", "calories_per_100g": 52, "protein_g": 0.3, "carbs_g": 13.8, "fat_g": 0.2, "fiber_g": 2.4, "source": "seed"},
    {"name": "Mango", "calories_per_100g": 60, "protein_g": 0.8, "carbs_g": 15.0, "fat_g": 0.4, "fiber_g": 1.6, "source": "seed"},
    {"name": "Orange", "calories_per_100g": 47, "protein_g": 0.9, "carbs_g": 11.8, "fat_g": 0.1, "fiber_g": 2.4, "source": "seed"},
    {"name": "Papaya", "calories_per_100g": 43, "protein_g": 0.5, "carbs_g": 11.0, "fat_g": 0.3, "fiber_g": 1.7, "source": "seed"},
    {"name": "Watermelon", "calories_per_100g": 30, "protein_g": 0.6, "carbs_g": 7.6, "fat_g": 0.2, "fiber_g": 0.4, "source": "seed"},
    {"name": "Guava", "calories_per_100g": 68, "protein_g": 2.6, "carbs_g": 14.3, "fat_g": 1.0, "fiber_g": 5.4, "source": "seed"},

    # ─── Proteins ─────────────────────────────────────────
    {"name": "Chicken Breast (Cooked)", "calories_per_100g": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "fiber_g": 0.0, "source": "seed"},
    {"name": "Boiled Egg", "calories_per_100g": 155, "protein_g": 13.0, "carbs_g": 1.1, "fat_g": 11.0, "fiber_g": 0.0, "source": "seed"},
    {"name": "Egg White", "calories_per_100g": 52, "protein_g": 11.0, "carbs_g": 0.7, "fat_g": 0.2, "fiber_g": 0.0, "source": "seed"},
    {"name": "Fish (Rohu)", "calories_per_100g": 97, "protein_g": 16.6, "carbs_g": 0.0, "fat_g": 3.3, "fiber_g": 0.0, "source": "seed"},
    {"name": "Salmon", "calories_per_100g": 208, "protein_g": 20.0, "carbs_g": 0.0, "fat_g": 13.0, "fiber_g": 0.0, "source": "seed"},
    {"name": "Tofu", "calories_per_100g": 76, "protein_g": 8.0, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.3, "source": "seed"},
    {"name": "Soya Chunks", "calories_per_100g": 345, "protein_g": 52.0, "carbs_g": 33.0, "fat_g": 0.5, "fiber_g": 13.0, "source": "seed"},

    # ─── Grains & Cereals ─────────────────────────────────
    {"name": "Oats", "calories_per_100g": 389, "protein_g": 16.9, "carbs_g": 66.3, "fat_g": 6.9, "fiber_g": 10.6, "source": "seed"},
    {"name": "Quinoa (Cooked)", "calories_per_100g": 120, "protein_g": 4.4, "carbs_g": 21.3, "fat_g": 1.9, "fiber_g": 2.8, "source": "seed"},
    {"name": "Whole Wheat Bread", "calories_per_100g": 247, "protein_g": 13.0, "carbs_g": 41.0, "fat_g": 3.4, "fiber_g": 6.0, "source": "seed"},
    {"name": "Sweet Potato", "calories_per_100g": 86, "protein_g": 1.6, "carbs_g": 20.0, "fat_g": 0.1, "fiber_g": 3.0, "source": "seed"},

    # ─── Nuts & Seeds ─────────────────────────────────────
    {"name": "Almonds", "calories_per_100g": 579, "protein_g": 21.2, "carbs_g": 21.6, "fat_g": 49.9, "fiber_g": 12.5, "source": "seed"},
    {"name": "Walnuts", "calories_per_100g": 654, "protein_g": 15.2, "carbs_g": 13.7, "fat_g": 65.2, "fiber_g": 6.7, "source": "seed"},
    {"name": "Peanuts", "calories_per_100g": 567, "protein_g": 25.8, "carbs_g": 16.1, "fat_g": 49.2, "fiber_g": 8.5, "source": "seed"},
    {"name": "Flax Seeds", "calories_per_100g": 534, "protein_g": 18.3, "carbs_g": 28.9, "fat_g": 42.2, "fiber_g": 27.3, "source": "seed"},
    {"name": "Makhana (Fox Nuts)", "calories_per_100g": 347, "protein_g": 9.7, "carbs_g": 76.9, "fat_g": 0.1, "fiber_g": 14.5, "source": "seed"},

    # ─── Beverages ────────────────────────────────────────
    {"name": "Green Tea (unsweetened)", "calories_per_100g": 1, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0, "source": "seed"},
    {"name": "Black Coffee (no sugar)", "calories_per_100g": 2, "protein_g": 0.1, "carbs_g": 0.0, "fat_g": 0.0, "fiber_g": 0.0, "source": "seed"},
    {"name": "Milk (Whole)", "calories_per_100g": 61, "protein_g": 3.2, "carbs_g": 4.8, "fat_g": 3.3, "fiber_g": 0.0, "source": "seed"},
    {"name": "Buttermilk / Chaas", "calories_per_100g": 40, "protein_g": 3.3, "carbs_g": 4.8, "fat_g": 0.9, "fiber_g": 0.0, "source": "seed"},
    {"name": "Coconut Water", "calories_per_100g": 19, "protein_g": 0.7, "carbs_g": 3.7, "fat_g": 0.2, "fiber_g": 1.1, "source": "seed"},

    # ─── Vegetables ───────────────────────────────────────
    {"name": "Spinach / Palak", "calories_per_100g": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4, "fiber_g": 2.2, "source": "seed"},
    {"name": "Broccoli", "calories_per_100g": 34, "protein_g": 2.8, "carbs_g": 7.0, "fat_g": 0.4, "fiber_g": 2.6, "source": "seed"},
    {"name": "Cucumber", "calories_per_100g": 15, "protein_g": 0.7, "carbs_g": 3.6, "fat_g": 0.1, "fiber_g": 0.5, "source": "seed"},
    {"name": "Tomato", "calories_per_100g": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2, "fiber_g": 1.2, "source": "seed"},
    {"name": "Avocado", "calories_per_100g": 160, "protein_g": 2.0, "carbs_g": 8.5, "fat_g": 14.7, "fiber_g": 6.7, "source": "seed"},

    # ─── Snacks (with barcodes for demo) ──────────────────
    {"name": "Lay's Classic Chips", "calories_per_100g": 536, "protein_g": 7.0, "carbs_g": 53.0, "fat_g": 35.0, "fiber_g": 3.0, "barcode": "012345678901", "source": "seed"},
    {"name": "Kurkure Masala Munch", "calories_per_100g": 520, "protein_g": 6.0, "carbs_g": 58.0, "fat_g": 30.0, "fiber_g": 2.0, "barcode": "890123456789", "source": "seed"},
    {"name": "Britannia Marie Gold", "calories_per_100g": 430, "protein_g": 7.0, "carbs_g": 70.0, "fat_g": 14.0, "fiber_g": 2.5, "barcode": "567890123456", "source": "seed"},
]


def seed():
    """Insert food items if table is empty."""
    app = create_app()
    with app.app_context():
        existing = FoodItem.query.count()
        if existing > 0:
            print(f"⚠️  Food items table already has {existing} records. Skipping seed.")
            return

        for item in FOOD_DATA:
            food = FoodItem(**item)
            db.session.add(food)

        db.session.commit()
        print(f"✅ Seeded {len(FOOD_DATA)} food items successfully!")


if __name__ == '__main__':
    seed()
