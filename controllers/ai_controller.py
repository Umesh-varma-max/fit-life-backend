"""
AI Diet Chat Controller.
Uses Groq when available and gracefully falls back to profile-based guidance.
"""

import os

from flask import jsonify

from models.health_profile import HealthProfile
from utils.bmi_calculator import get_bmi_category
from utils.recommendation_engine import generate_recommendation

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def diet_chat(user_id: int, message: str):
    """Send user message to Groq AI with health context and safe fallback."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    system_prompt = _build_system_prompt(profile)

    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not GROQ_AVAILABLE or not api_key:
        return _fallback_response(message, profile)

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv('GROQ_TEXT_MODEL', 'llama3-70b-8192'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=512,
            temperature=0.5
        )

        reply = response.choices[0].message.content
        if not reply:
            return _fallback_response(message, profile)

        return jsonify({
            "status": "success",
            "reply": reply,
            "speak": True
        }), 200
    except Exception:
        return _fallback_response(message, profile)


def _build_system_prompt(profile) -> str:
    if not profile:
        return (
            "You are a helpful AI diet and fitness assistant for FitLife. "
            "Give concise, practical, personalized advice. Prefer Indian food options when relevant. "
            "Keep answers under 5 sentences unless the user asks for a detailed plan."
        )

    bmi_value = float(profile.bmi) if profile.bmi is not None else None
    bmi_cat = get_bmi_category(bmi_value) if bmi_value is not None else 'Unknown'
    return f"""You are a professional AI diet and fitness assistant for the FitLife app.
The user profile is:
- Age: {profile.age}
- Gender: {profile.gender}
- BMI: {bmi_value if bmi_value is not None else 'N/A'} ({bmi_cat})
- Fitness Goal: {profile.fitness_goal.replace('_', ' ').title()}
- Food Preference: {profile.food_habits.replace('-', ' ').title()}
- Daily Calorie Target: {profile.daily_calories} kcal
- Activity Level: {profile.activity_level.title()}

Give practical, evidence-based advice with concrete meal and activity suggestions.
Keep responses short unless the user explicitly asks for a full plan.
Prefer Indian food options when useful."""


def _fallback_response(message: str, profile=None):
    """Return a personalized rule-based answer when live AI is unavailable."""
    msg_lower = message.lower()
    recommendations = generate_recommendation(profile) if profile else None
    diet_plan = recommendations.get('diet_plan', {}) if recommendations else {}
    daily_calories = recommendations.get('daily_calories') if recommendations else None
    bmi_text = ''
    if profile and profile.bmi is not None:
        bmi_text = f"Your BMI category is {get_bmi_category(float(profile.bmi))}. "

    if any(word in msg_lower for word in ['breakfast', 'morning']):
        breakfast = diet_plan.get('breakfast')
        if breakfast:
            reply = f"{bmi_text}For breakfast, go with {breakfast['meal']} at about {breakfast['kcal']} kcal."
        else:
            reply = "For breakfast, try oats with fruit and a protein source like eggs, paneer, or yogurt."
    elif any(word in msg_lower for word in ['lunch', 'afternoon']):
        lunch = diet_plan.get('lunch')
        if lunch:
            reply = f"{bmi_text}Lunch can be {lunch['meal']} at about {lunch['kcal']} kcal."
        else:
            reply = "For lunch, build your plate around lean protein, vegetables, and a controlled portion of carbs."
    elif any(word in msg_lower for word in ['dinner', 'night', 'evening']):
        dinner = diet_plan.get('dinner')
        if dinner:
            reply = f"{bmi_text}Dinner can be {dinner['meal']} at about {dinner['kcal']} kcal. Try to keep it light and early."
        else:
            reply = "For dinner, keep it lighter than lunch and include vegetables plus protein."
    elif any(word in msg_lower for word in ['snack', 'hungry']):
        snack = diet_plan.get('snack')
        if snack:
            reply = f"{bmi_text}A good snack for you is {snack['meal']} at about {snack['kcal']} kcal."
        else:
            reply = "Healthy snacks include fruit with nuts, yogurt, roasted chana, or sprouts."
    elif any(word in msg_lower for word in ['weight loss', 'lose weight', 'fat']):
        reply = f"{bmi_text}For weight loss, stay near {daily_calories or 1800} kcal per day, prioritize protein, walk daily, and keep portions controlled."
    elif any(word in msg_lower for word in ['muscle', 'gain', 'bulk']):
        reply = f"{bmi_text}For muscle gain, stay near {daily_calories or 2400} kcal per day, aim for high protein, and focus on progressive overload."
    elif any(word in msg_lower for word in ['calorie', 'kcal', 'diet plan', 'meal plan']):
        if diet_plan:
            breakfast = diet_plan.get('breakfast', {}).get('meal', 'a balanced breakfast')
            lunch = diet_plan.get('lunch', {}).get('meal', 'a balanced lunch')
            dinner = diet_plan.get('dinner', {}).get('meal', 'a balanced dinner')
            reply = (
                f"{bmi_text}Your current target is about {daily_calories or 2000} kcal/day. "
                f"A good structure is breakfast: {breakfast}; lunch: {lunch}; dinner: {dinner}."
            )
        else:
            reply = "A balanced day should include a protein-rich breakfast, vegetable-heavy lunch, lighter dinner, and one smart snack."
    else:
        reply = (
            f"{bmi_text}Your current calorie target is about {daily_calories or 2000} kcal/day. "
            "Ask me for breakfast, lunch, dinner, snack, or a goal-based plan and I will personalize it."
        )

    return jsonify({
        "status": "success",
        "reply": reply,
        "speak": True
    }), 200
