# controllers/ai_controller.py
"""
AI Diet Chat Controller — uses Groq API (FREE) with Llama 3 70B model.
Builds a personalized system prompt from the user's health profile.
"""

import os
from flask import jsonify
from models.health_profile import HealthProfile
from utils.bmi_calculator import get_bmi_category

# Try to import groq; graceful fallback if not installed
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


def diet_chat(user_id: int, message: str):
    """Send user message to Groq AI with their health context."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()

    # Build personalized system prompt
    if profile:
        bmi_cat = get_bmi_category(float(profile.bmi)) if profile.bmi else 'Unknown'
        system_prompt = f"""You are a professional AI diet and fitness assistant for the FitLife app.
The user you are helping has the following profile:
- Age: {profile.age}, Gender: {profile.gender}
- BMI: {float(profile.bmi) if profile.bmi else 'N/A'} ({bmi_cat})
- Fitness Goal: {profile.fitness_goal.replace('_', ' ').title()}
- Food Preference: {profile.food_habits.replace('-', ' ').title()}
- Daily Calorie Target: {profile.daily_calories} kcal
- Activity Level: {profile.activity_level.title()}

Provide short, practical, personalized advice.
Keep responses under 4 sentences unless detailed meal plans are requested.
Be friendly, encouraging, and evidence-based.
Prefer Indian food options when suggesting meals."""
    else:
        system_prompt = (
            "You are a helpful AI diet and fitness assistant. "
            "Give friendly, practical advice. Prefer Indian food options when relevant."
        )

    # Check if Groq is available
    api_key = os.getenv('GROQ_API_KEY', '')
    if not GROQ_AVAILABLE or not api_key:
        return _fallback_response(message)

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=512,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        return jsonify({
            "status": "success",
            "reply": reply,
            "speak": True
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"AI service error: {str(e)}"
        }), 500


def _fallback_response(message: str):
    """Fallback responses when Groq API is not available."""
    msg_lower = message.lower()

    if any(word in msg_lower for word in ['breakfast', 'morning']):
        reply = "For a healthy breakfast, try oats with banana and green tea (~350 kcal). Add a boiled egg for extra protein!"
    elif any(word in msg_lower for word in ['lunch', 'afternoon']):
        reply = "For lunch, try grilled chicken/paneer with brown rice and salad (~550 kcal). Stay hydrated!"
    elif any(word in msg_lower for word in ['dinner', 'night', 'evening']):
        reply = "For dinner, keep it light — dal + roti + sautéed veggies (~450 kcal). Avoid heavy meals 2 hours before sleep."
    elif any(word in msg_lower for word in ['snack', 'hungry']):
        reply = "Healthy snack options: mixed nuts + fruit (~180 kcal), sprout chaat, or yogurt with berries."
    elif any(word in msg_lower for word in ['weight loss', 'lose weight', 'fat']):
        reply = "For weight loss, maintain a 500 kcal daily deficit. Focus on protein-rich meals, drink 3L water, and add 30 min cardio daily."
    elif any(word in msg_lower for word in ['muscle', 'gain', 'bulk']):
        reply = "For muscle gain, eat 1.6-2.2g protein per kg bodyweight. Focus on compound lifts and get 7-8 hours sleep."
    else:
        reply = "I recommend tracking your meals, staying hydrated (3L/day), and getting 30 minutes of exercise daily. Would you like a specific meal suggestion?"

    return jsonify({
        "status": "success",
        "reply": reply,
        "speak": True
    }), 200
