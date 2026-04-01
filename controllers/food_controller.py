from datetime import date
from typing import Optional

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.food_item import FoodItem
from utils.ai_structured import groq_json_vision


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


def _find_food(food_name: str = None):
    """Find a food by exact or partial name."""
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
        'estimated_calories': round(float(food.calories_per_100g or 0) * multiplier, 1),
        'protein_g': round(float(food.protein_g or 0) * multiplier, 1),
        'carbs_g': round(float(food.carbs_g or 0) * multiplier, 1),
        'fat_g': round(float(food.fat_g or 0) * multiplier, 1),
        'fiber_g': round(float(food.fiber_g or 0) * multiplier, 1),
    }


def _build_food_feedback(calories: float, protein_g: float, fiber_g: float) -> str:
    """Return quick meal feedback based on calories and macros."""
    if calories >= 500:
        return "High-calorie meal. Balance the rest of the day with lighter meals and extra movement."
    if protein_g >= 20 and calories <= 400:
        return "Strong protein choice. Good support for recovery and fullness."
    if fiber_g >= 5 and calories <= 300:
        return "Fiber-rich choice. Great for satiety and steadier digestion."
    if calories <= 150:
        return "Light intake. This works well as a snack or small add-on meal."
    return "Balanced meal estimate. Keep portions aligned with your calorie target."


def _meal_log_payload(food_name: str, meal_time: Optional[str], analysis: dict, timestamp: Optional[str] = None) -> dict:
    return {
        "entry_type": "photo_food_analysis",
        "food_name": food_name,
        "serving_estimate": analysis.get('serving_estimate', '1 serving'),
        "estimated_calories": analysis.get('estimated_calories', 0),
        "protein_g": analysis.get('protein_g', 0),
        "carbs_g": analysis.get('carbs_g', 0),
        "fat_g": analysis.get('fat_g', 0),
        "meal_time": meal_time or 'meal',
        "logged_at": timestamp or date.today().isoformat()
    }


def _persist_meal_log(user_id: int, food_name: str, meal_time: Optional[str], analysis: dict, log_date: Optional[str]):
    log = ActivityLog(
        user_id=user_id,
        log_date=date.fromisoformat(log_date) if log_date else date.today(),
        log_type='meal',
        description=f"{(meal_time or 'meal').title()}: {food_name}",
        calories_in=int(round(float(analysis.get('estimated_calories', 0) or 0))),
        details=_meal_log_payload(food_name, meal_time, analysis, log_date)
    )
    db.session.add(log)
    db.session.commit()
    return log


def analyze_food_name(food_name: str, quantity_g=100, meal_time: str = None,
                      should_log: bool = False, log_date: str = None, user_id: int = None):
    """
    Analyze food by direct name matching and optionally persist as a meal log.
    """
    food, matched_by = _find_food(food_name=food_name)

    if not food:
        return {"status": "error", "message": "Food not found for the given name"}, 404

    try:
        quantity_g = float(quantity_g or 100)
    except (TypeError, ValueError):
        quantity_g = 100
    quantity_g = max(1.0, quantity_g)

    nutrients = _scaled_macros(food, quantity_g)
    response = {
        "status": "success",
        "food": {
            "name": food.name,
            "matched_by": matched_by,
            "serving_estimate": f"{int(quantity_g)} g",
            "quantity_g": quantity_g,
            **nutrients,
            "feedback": _build_food_feedback(
                calories=nutrients['estimated_calories'],
                protein_g=nutrients['protein_g'],
                fiber_g=nutrients['fiber_g']
            )
        }
    }

    if should_log and user_id:
        log = _persist_meal_log(user_id, food.name, meal_time, response['food'], log_date)
        response["meal_log"] = {"logged": True, "log_id": log.id}

    return response, 200


def _fallback_photo_analysis(filename: str, meal_time: str = None) -> dict:
    """Fallback estimate when AI image analysis is unavailable."""
    guessed_name = (filename.rsplit('.', 1)[0] if filename else 'Meal').replace('-', ' ').replace('_', ' ').title() or 'Meal'
    estimated_calories = 320
    analysis = {
        "food_name": guessed_name,
        "serving_estimate": "1 serving",
        "estimated_calories": estimated_calories,
        "protein_g": 12,
        "carbs_g": 34,
        "fat_g": 11
    }
    analysis["feedback"] = _build_food_feedback(estimated_calories, analysis["protein_g"], 3)
    analysis["meal_time"] = meal_time or 'meal'
    analysis["source"] = "fallback"
    return analysis


def analyze_food_photo(image_bytes: bytes, mime_type: str, filename: str = None, meal_time: str = None,
                       should_log: bool = False, log_date: str = None, user_id: int = None):
    """
    Analyze a real food photo using an AI vision model and optionally log it.
    """
    system_prompt = (
        "You analyze food photos for the FitLife app. "
        "Return pure JSON only with this exact shape: "
        "{\"food_name\": string, \"serving_estimate\": string, \"estimated_calories\": number, "
        "\"protein_g\": number, \"carbs_g\": number, \"fat_g\": number}. "
        "Do not include markdown fences or extra explanation."
    )
    user_prompt = (
        "Identify the primary food item in this image and estimate a realistic serving size and macros. "
        "If the image contains multiple foods, summarize the main plate total."
    )

    try:
        analysis = groq_json_vision(system_prompt, user_prompt, image_bytes=image_bytes, mime_type=mime_type)
        food_name = str(analysis.get('food_name') or 'Unknown Meal').strip()
        payload = {
            "food_name": food_name,
            "serving_estimate": str(analysis.get('serving_estimate') or '1 serving'),
            "estimated_calories": round(float(analysis.get('estimated_calories') or 0), 1),
            "protein_g": round(float(analysis.get('protein_g') or 0), 1),
            "carbs_g": round(float(analysis.get('carbs_g') or 0), 1),
            "fat_g": round(float(analysis.get('fat_g') or 0), 1),
            "meal_time": meal_time or 'meal',
            "source": "ai_vision"
        }
    except Exception:
        payload = _fallback_photo_analysis(filename=filename, meal_time=meal_time)
        food_name = payload["food_name"]

    payload["feedback"] = _build_food_feedback(
        calories=float(payload.get('estimated_calories') or 0),
        protein_g=float(payload.get('protein_g') or 0),
        fiber_g=0
    )

    response = {
        "status": "success",
        "food": payload
    }

    if should_log and user_id:
        log = _persist_meal_log(user_id, food_name, meal_time, payload, log_date)
        response["meal_log"] = {"logged": True, "log_id": log.id}

    return response, 200
