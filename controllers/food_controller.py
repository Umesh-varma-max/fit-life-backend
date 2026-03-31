from datetime import date

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.food_item import FoodItem


def search_food(query: str):
    """Search food items by name (case-insensitive LIKE query)."""
    if not query or len(query.strip()) < 2:
        return jsonify({"status": "error", "message": "Search query too short (min 2 chars)"}), 400

    results = FoodItem.query.filter(
        FoodItem.name.ilike(f'%{query.strip()}%')
    ).limit(20).all()

    return jsonify({
        "status": "success",
        "results": [f.to_dict() for f in results]
    }), 200


def _find_food(barcode: str = None, food_name: str = None):
    """Find a food by barcode first, then by exact/partial name."""
    if barcode:
        return FoodItem.query.filter_by(barcode=barcode.strip()).first(), 'barcode'

    normalized_name = (food_name or '').strip()
    if not normalized_name:
        return None, None

    exact_match = FoodItem.query.filter(FoodItem.name.ilike(normalized_name)).first()
    if exact_match:
        return exact_match, 'name_exact'

    partial_match = FoodItem.query.filter(
        FoodItem.name.ilike(f'%{normalized_name}%')
    ).order_by(FoodItem.name.asc()).first()
    if partial_match:
        return partial_match, 'name_partial'

    return None, None


def _scaled_macros(food: FoodItem, quantity_g: float) -> dict:
    """Scale nutrient values from per-100g to the requested quantity."""
    multiplier = quantity_g / 100.0
    return {
        'calories': round(float(food.calories_per_100g or 0) * multiplier, 1),
        'protein_g': round(float(food.protein_g or 0) * multiplier, 1),
        'carbs_g': round(float(food.carbs_g or 0) * multiplier, 1),
        'fat_g': round(float(food.fat_g or 0) * multiplier, 1),
        'fiber_g': round(float(food.fiber_g or 0) * multiplier, 1),
    }


def _build_food_feedback(calories: float, protein_g: float, fiber_g: float) -> str:
    """Return quick meal feedback based on calories and macros."""
    if calories >= 500:
        return "High-calorie meal. Keep portions in check or pair it with lighter meals later."
    if protein_g >= 20 and calories <= 400:
        return "Strong protein choice. This supports fullness and muscle recovery well."
    if fiber_g >= 5 and calories <= 300:
        return "Fiber-rich choice. Good for satiety and steadier digestion."
    if calories <= 150:
        return "Light intake. This works well as a snack or small add-on meal."
    return "Balanced choice. It can fit well when matched to your daily calorie target."


def scan_food(barcode: str = None, food_name: str = None, quantity_g=100, meal_time: str = None,
              should_log: bool = False, log_date: str = None):
    """
    Analyze a scanned food and optionally log it as a meal entry.
    Supports barcode scans and direct food-name matching.
    """
    food, matched_by = _find_food(barcode=barcode, food_name=food_name)

    if not food:
        return {"status": "error", "message": "Food not found for the given scan input"}, 404

    try:
        quantity_g = float(quantity_g or 100)
    except (TypeError, ValueError):
        quantity_g = 100
    quantity_g = max(1.0, quantity_g)

    nutrients = _scaled_macros(food, quantity_g)
    feedback = _build_food_feedback(
        calories=nutrients['calories'],
        protein_g=nutrients['protein_g'],
        fiber_g=nutrients['fiber_g']
    )

    result = food.to_dict()
    result.update({
        'matched_by': matched_by,
        'quantity_g': quantity_g,
        'estimated_calories': nutrients['calories'],
        'protein_g_for_quantity': nutrients['protein_g'],
        'carbs_g_for_quantity': nutrients['carbs_g'],
        'fat_g_for_quantity': nutrients['fat_g'],
        'fiber_g_for_quantity': nutrients['fiber_g'],
        'meal_time': meal_time or 'unspecified',
        'feedback': feedback
    })

    response = {
        "status": "success",
        "food": result
    }

    if should_log:
        log = ActivityLog(
            user_id=None,  # set by route after instantiation for safer explicitness
            log_date=date.fromisoformat(log_date) if log_date else date.today(),
            log_type='meal',
            description=f"{(meal_time or 'meal').title()}: {food.name} ({int(quantity_g)}g)",
            calories_in=int(round(nutrients['calories']))
        )
        response['pending_log'] = log

    return response, 200


def finalize_food_log(user_id: int, response_payload: dict):
    """Persist a pending meal log created during food analysis."""
    pending_log = response_payload.pop('pending_log', None)
    if not pending_log:
        return jsonify(response_payload), 200

    pending_log.user_id = user_id
    db.session.add(pending_log)
    db.session.commit()

    response_payload['meal_log'] = {
        'logged': True,
        'log_id': pending_log.id
    }
    return jsonify(response_payload), 200


def scan_barcode(barcode: str):
    """Backward-compatible barcode-only wrapper."""
    response_payload, status_code = scan_food(barcode=barcode)
    return jsonify(response_payload), status_code
