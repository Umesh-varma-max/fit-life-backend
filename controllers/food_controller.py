from datetime import date
from pathlib import Path
import re

from flask import jsonify

from extensions import db
from models.activity_log import ActivityLog
from models.food_item import FoodItem
from utils.ai_structured import gemini_json_vision, groq_json_vision

MAX_IMAGE_SIZE_BYTES = 8 * 1024 * 1024
ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/webp',
    'image/heic',
    'image/heif'
}
VISION_SYSTEM_PROMPT = (
    'Act as an advanced food recognition and nutrition estimation AI for the FitLife app. '
    'Analyze the image and provide the most realistic, scientifically grounded nutrition values. '
    'Identify the exact food item or branded packaged food when visible. '
    'Estimate portion size from visual cues or packaging. '
    'Use real-world nutrition knowledge and do not invent exaggerated protein values. '
    'Return pure JSON only with this exact shape: '
    '{"food_name": string, "serving_estimate": string, "estimated_calories": number, '
    '"protein_g": number, "carbs_g": number, "fat_g": number, "confidence": string, '
    '"notes": string[]}.'
)


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


def _fallback_analysis(food_hint: str = '', filename: str = '') -> dict:
    """Fallback to local nutrition data only when there is a believable DB match."""
    hint = (food_hint or '').replace('-', ' ').replace('_', ' ').strip()

    if not hint:
        stem = Path(filename or '').stem.replace('-', ' ').replace('_', ' ').strip()
        cleaned_tokens = [
            token for token in re.findall(r'[A-Za-z]{3,}', stem)
            if token.lower() not in {'img', 'image', 'photo', 'scan', 'meal', 'capture', 'camera'}
        ]
        hint = ' '.join(cleaned_tokens[:4]).strip()

    food, matched_by = _find_food(food_name=hint) if hint else (None, None)

    if food:
        nutrients = _scaled_macros(food, 100)
        return {
            'food_name': food.name,
            'serving_estimate': '100 g serving',
            'estimated_calories': nutrients['calories'],
            'protein_g': nutrients['protein_g'],
            'carbs_g': nutrients['carbs_g'],
            'fat_g': nutrients['fat_g'],
            'confidence': 'Fallback',
            'notes': [f'Estimated using local nutrition data ({matched_by}).']
        }

    return None


def _extract_serving_grams(serving_estimate: str):
    """Try to extract gram quantity from strings like '150 g serving'."""
    if not serving_estimate:
        return None

    match = re.search(r'(\d+(?:\.\d+)?)\s*g\b', serving_estimate.lower())
    if not match:
        return None

    try:
        grams = float(match.group(1))
    except ValueError:
        return None
    return grams if grams > 0 else None


def _enrich_analysis_with_food_db(ai_vision: dict) -> dict:
    """Blend AI vision output with local DB nutrition when a close match exists."""
    food_name = (ai_vision.get('food_name') or '').strip()
    if not food_name:
        return ai_vision

    food, matched_by = _find_food(food_name=food_name)
    if not food:
        return ai_vision

    grams = _extract_serving_grams(ai_vision.get('serving_estimate'))
    notes = list(ai_vision.get('notes') or [])

    if grams:
        nutrients = _scaled_macros(food, grams)
        ai_vision['estimated_calories'] = nutrients['calories']
        ai_vision['protein_g'] = nutrients['protein_g']
        ai_vision['carbs_g'] = nutrients['carbs_g']
        ai_vision['fat_g'] = nutrients['fat_g']
        notes.append(f'Nutrition refined using FitLife food database ({matched_by}).')
    else:
        notes.append(f'Closest FitLife food match found: {food.name}.')

    ai_vision['notes'] = notes
    return ai_vision


def analyze_food_photo(file_storage, food_hint: str = None):
    """Analyze a real food photo using Groq vision and return nutrition JSON."""
    if not file_storage:
        return {"status": "error", "message": "A photo upload is required"}, 400

    image_bytes = file_storage.read()
    mime_type = (file_storage.mimetype or '').lower()

    if not image_bytes:
        return {"status": "error", "message": "Uploaded photo is empty"}, 400
    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        return {"status": "error", "message": "Image is too large. Please upload a file under 8 MB."}, 400
    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        return {"status": "error", "message": "Unsupported image type. Please upload JPG, PNG, WEBP, or HEIC."}, 400

    user_prompt = (
        'Identify the primary food item in this image and estimate a realistic serving size and macros. '
        'If the image contains a branded package, read the visible product name and use that to infer realistic nutrition. '
        'If the image contains multiple foods, summarize the main plate total. '
        f'Optional user hint: {(food_hint or "none").strip() or "none"}.'
    )

    try:
        ai_vision = gemini_json_vision(
            system_prompt=VISION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            image_bytes=image_bytes,
            mime_type=mime_type
        )
    except Exception:
        try:
            ai_vision = groq_json_vision(
                system_prompt=VISION_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                image_bytes=image_bytes,
                mime_type=mime_type
            )
        except Exception:
            ai_vision = _fallback_analysis(food_hint=food_hint, filename=file_storage.filename)

    if ai_vision:
        ai_vision = _enrich_analysis_with_food_db(ai_vision)

    if not ai_vision:
        return {
            "status": "error",
            "message": (
                "Could not confidently identify this food from the photo. "
                "Try a clearer image, capture the package name, or add a food hint."
            )
        }, 422

    estimated_calories = float(ai_vision.get('estimated_calories') or 0)
    protein_g = float(ai_vision.get('protein_g') or 0)
    carbs_g = float(ai_vision.get('carbs_g') or 0)
    fat_g = float(ai_vision.get('fat_g') or 0)

    normalized_analysis = {
        "food_name": ai_vision.get('food_name') or 'Unknown Meal',
        "name": ai_vision.get('food_name') or 'Unknown Meal',
        "serving_estimate": ai_vision.get('serving_estimate') or '1 serving',
        "serving": ai_vision.get('serving_estimate') or '1 serving',
        "estimated_calories": round(estimated_calories, 1),
        "calories": round(estimated_calories, 1),
        "protein_g": round(protein_g, 1),
        "protein": round(protein_g, 1),
        "carbs_g": round(carbs_g, 1),
        "carbs": round(carbs_g, 1),
        "fat_g": round(fat_g, 1),
        "fats": round(fat_g, 1),
        "confidence": ai_vision.get('confidence') or 'Estimated',
        "notes": ai_vision.get('notes') or [],
        "feedback": _build_food_feedback(estimated_calories, protein_g, 0),
        "source": "ai_vision"
    }

    return {
        "status": "success",
        "analysis": normalized_analysis,
        "food": normalized_analysis
    }, 200


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
