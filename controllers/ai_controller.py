"""AI planner controller with strong profile-aware fallback behavior."""

from __future__ import annotations

import os
from datetime import date, timedelta

from flask import jsonify

from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.recommendation import Recommendation
from utils.bmi_calculator import get_bmi_category
from utils.recommendation_engine import generate_recommendation
from utils.workout_planner import generate_profile_workout_plan

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


try:
    from models.workout_session import WorkoutSession
except Exception:
    WorkoutSession = None


TOPIC_SUGGESTIONS = {
    'breakfast': ['Ask for a high-protein breakfast', 'Ask how to reduce cravings today', 'Ask for a 500 kcal meal idea'],
    'lunch': ['Ask for a lunch idea under your calorie target', 'Ask for veg/non-veg swaps', 'Ask what to eat before workout'],
    'dinner': ['Ask for a light dinner', 'Ask what to eat after 8 PM', 'Ask for a recovery dinner'],
    'snack': ['Ask for a smart snack', 'Ask what to eat when hungry', 'Ask for a sweet craving alternative'],
    'workout': ['Ask for today’s workout', 'Ask how long your goal may take', 'Ask which exercise to focus on'],
    'progress': ['Ask how your week is going', 'Ask how many calories you have left', 'Ask for a plan reset'],
    'hydration': ['Ask how much water to drink', 'Ask for hydration habits', 'Ask how water affects weight loss'],
    'recovery': ['Ask how sleep affects your goal', 'Ask for a recovery routine', 'Ask what to do on rest day'],
    'body_metrics': ['Ask what your BMI means', 'Ask about body fat percentage', 'Ask how to improve your category'],
    'general': ['Ask for your meal plan', 'Ask for your workout plan', 'Ask for a daily routine']
}


def diet_chat(user_id: int, message: str):
    """Send user message to Groq AI with health context and a rich fallback."""
    topic = _detect_topic(message)
    context = _build_chat_context(user_id, topic)
    system_prompt = _build_system_prompt(context)
    api_key = os.getenv('GROQ_API_KEY', '').strip()

    if not GROQ_AVAILABLE or not api_key:
        return _fallback_response(message, context, topic, provider='rule_fallback')

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv('GROQ_TEXT_MODEL', 'llama3-70b-8192'),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=420,
            temperature=0.45
        )
        reply = (response.choices[0].message.content or '').strip()
        if not reply:
            return _fallback_response(message, context, topic, provider='rule_fallback')

        return jsonify({
            "status": "success",
            "reply": reply,
            "speak": True,
            "provider": "groq",
            "topic": topic,
            "suggestions": TOPIC_SUGGESTIONS.get(topic, TOPIC_SUGGESTIONS['general'])
        }), 200
    except Exception:
        return _fallback_response(message, context, topic, provider='rule_fallback')


def _build_chat_context(user_id: int, topic: str) -> dict:
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    recommendation = Recommendation.query.filter_by(user_id=user_id).first()
    generated = None
    if profile and not recommendation:
        generated = generate_recommendation(profile)

    should_load_workout = topic in {'workout', 'progress', 'general'}
    if profile and should_load_workout:
        workout_plan = generate_profile_workout_plan(profile)
    else:
        workout_plan = None

    today = date.today()
    today_logs = ActivityLog.query.filter_by(user_id=user_id, log_date=today).all()
    recent_logs = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.log_date >= today - timedelta(days=6)
    ).all()

    active_session = None
    if WorkoutSession is not None and should_load_workout:
        session = WorkoutSession.query.filter_by(user_id=user_id, status='active').order_by(WorkoutSession.started_at.desc()).first()
        active_session = session.to_dict() if session else None

    calories_in = sum(log.calories_in or 0 for log in today_logs)
    calories_out = sum(log.calories_out or 0 for log in today_logs)
    water_ml = sum(log.water_ml or 0 for log in today_logs)
    sleep_hours = sum(float(log.sleep_hours or 0) for log in today_logs)
    workout_count_week = sum(1 for log in recent_logs if log.log_type == 'workout')

    return {
        'profile': profile,
        'recommendation': recommendation.to_dict() if recommendation else generated,
        'workout_plan': workout_plan,
        'active_session': active_session,
        'today': {
            'calories_in': calories_in,
            'calories_out': calories_out,
            'water_ml': water_ml,
            'sleep_hours': round(sleep_hours, 1),
            'meal_logs': [log for log in today_logs if log.log_type == 'meal'],
            'workout_logs': [log for log in today_logs if log.log_type == 'workout']
        },
        'week': {
            'workout_count': workout_count_week,
            'days_with_logs': len({str(log.log_date) for log in recent_logs})
        }
    }


def _build_system_prompt(context: dict) -> str:
    profile = context.get('profile')
    recommendation = context.get('recommendation') or {}
    workout_plan = context.get('workout_plan') or {}
    today = context.get('today') or {}

    if not profile:
        return (
            "You are the FitLife AI planner. Give concise, practical meal, workout, and wellness guidance. "
            "If the user has no profile yet, encourage them to create one so the app can personalize calories, workouts, and progress."
        )

    bmi_value = float(profile.bmi) if profile.bmi is not None else None
    bmi_cat = get_bmi_category(bmi_value) if bmi_value is not None else 'Unknown'
    body_fat = float(getattr(profile, 'body_fat_percentage', 0) or 0)
    body_fat_category = getattr(profile, 'body_fat_category', 'Unknown')
    today_plan = workout_plan.get('today_plan') or {}
    today_exercises = today_plan.get('exercises', [])
    meal_plan = recommendation.get('diet_plan') or {}
    breakfast = meal_plan.get('breakfast', {})
    lunch = meal_plan.get('lunch', {})
    dinner = meal_plan.get('dinner', {})
    snack = meal_plan.get('snack', {})

    return f"""
You are the FitLife AI planner, a concise but premium health coach inside the app.

User profile:
- Age: {profile.age}
- Gender: {profile.gender}
- Fitness goal: {profile.fitness_goal.replace('_', ' ').title()}
- Activity level: {profile.activity_level.title()}
- BMI: {bmi_value if bmi_value is not None else 'N/A'} ({bmi_cat})
- Body fat: {body_fat or 'N/A'}% ({body_fat_category})
- Daily calorie target: {profile.daily_calories or recommendation.get('daily_calories') or 'N/A'} kcal

Current day context:
- Calories consumed today: {today.get('calories_in', 0)}
- Calories burned today: {today.get('calories_out', 0)}
- Water today: {today.get('water_ml', 0)} ml
- Sleep today: {today.get('sleep_hours', 0)} hours

Meal plan highlights:
- Breakfast: {breakfast.get('meal', 'Not set')}
- Lunch: {lunch.get('meal', 'Not set')}
- Dinner: {dinner.get('meal', 'Not set')}
- Snack: {snack.get('meal', 'Not set')}

Workout plan highlights:
- Goal label: {workout_plan.get('goal_label', 'Adaptive Fitness Plan')}
- Estimated goal period: {workout_plan.get('goal_eta_weeks', 'N/A')} weeks
- Today's session: {today_plan.get('plan_name', 'Not available')}
- Today's exercise count: {len(today_exercises)}

Response style:
- Be practical, specific, and supportive.
- Give app-aware answers using the profile and plan above.
- Prefer 3-6 short sentences or a compact bullet list.
- Mention concrete foods, calories, or exercises when useful.
- If the user asks for motivation, keep it crisp and uplifting.
- Prefer Indian-friendly meal suggestions when relevant.
""".strip()


def _detect_topic(message: str) -> str:
    msg = message.lower()
    if any(word in msg for word in ['breakfast', 'morning']):
        return 'breakfast'
    if any(word in msg for word in ['lunch', 'afternoon']):
        return 'lunch'
    if any(word in msg for word in ['dinner', 'night', 'evening']):
        return 'dinner'
    if any(word in msg for word in ['snack', 'hungry', 'craving']):
        return 'snack'
    if any(word in msg for word in ['workout', 'exercise', 'gym', 'train', 'timer', 'session']):
        return 'workout'
    if any(word in msg for word in ['progress', 'streak', 'today', 'week', 'track']):
        return 'progress'
    if any(word in msg for word in ['water', 'hydrate', 'hydration']):
        return 'hydration'
    if any(word in msg for word in ['sleep', 'rest', 'recovery']):
        return 'recovery'
    if any(word in msg for word in ['bmi', 'body fat', 'fat percentage', 'weight category']):
        return 'body_metrics'
    return 'general'


def _meal_text(meal: dict, fallback: str) -> str:
    if meal and meal.get('meal'):
        return f"{meal['meal']} ({meal.get('kcal', 0)} kcal)"
    return fallback


def _format_today_workout(workout_plan: dict) -> str:
    if not workout_plan:
        return "Your workout plan will appear after your health profile is saved."
    today_plan = workout_plan.get('today_plan') or {}
    if not today_plan:
        return "I don't have a workout loaded for today yet."
    exercises = today_plan.get('exercises', [])
    if not exercises:
        return f"Today is {today_plan.get('plan_name', 'a recovery day')}."
    exercise_bits = []
    for exercise in exercises[:3]:
        timer = exercise.get('duration_seconds') or 0
        timer_text = f"{timer}s" if timer else f"{exercise.get('estimated_duration_min', 0)} min"
        exercise_bits.append(f"{exercise.get('name')} ({timer_text})")
    return f"{today_plan.get('plan_name')}: " + ", ".join(exercise_bits)


def _fallback_response(message: str, context: dict, topic: str, provider: str):
    profile = context.get('profile')
    recommendation = context.get('recommendation') or {}
    workout_plan = context.get('workout_plan') or {}
    today = context.get('today') or {}
    meal_plan = recommendation.get('diet_plan') or {}
    daily_calories = recommendation.get('daily_calories') or (profile.daily_calories if profile else None) or 2000

    if not profile:
        reply = (
            "I can help with meals, workouts, and progress, but I need your health profile first. "
            "Complete age, height, weight, activity level, and goal so I can personalize calories and workouts."
        )
        return _build_response(reply, provider, topic)

    bmi_text = ''
    if profile.bmi is not None:
        bmi_text = f"Your BMI is {float(profile.bmi):.1f} ({get_bmi_category(float(profile.bmi))}). "
    body_fat_text = ''
    if getattr(profile, 'body_fat_percentage', None) is not None:
        body_fat_text = f"Body fat is about {float(profile.body_fat_percentage):.1f}% ({profile.body_fat_category}). "

    if topic == 'breakfast':
        reply = (
            f"{bmi_text}{body_fat_text}For breakfast, go with {_meal_text(meal_plan.get('breakfast'), 'oats, eggs, fruit, or curd with nuts')}. "
            f"Keep it protein-focused so you stay fuller and more consistent with your {profile.fitness_goal.replace('_', ' ')} goal."
        )
    elif topic == 'lunch':
        reply = (
            f"{bmi_text}A good lunch for you is {_meal_text(meal_plan.get('lunch'), 'roti or rice with vegetables and a lean protein')}. "
            "Aim for a balanced plate instead of a heavy carb-only meal."
        )
    elif topic == 'dinner':
        reply = (
            f"{bmi_text}Dinner should stay controlled and recovery-friendly. "
            f"Try {_meal_text(meal_plan.get('dinner'), 'paneer/chicken, vegetables, and a light carb portion')}."
        )
    elif topic == 'snack':
        reply = (
            f"{bmi_text}For snacks, choose {_meal_text(meal_plan.get('snack'), 'fruit, yogurt, roasted chana, or nuts in moderation')}. "
            "That fits your calorie target much better than random packaged snacks."
        )
    elif topic == 'workout':
        eta = workout_plan.get('goal_eta_weeks')
        reply = (
            f"{bmi_text}{body_fat_text}Your current plan is {workout_plan.get('goal_label', 'an adaptive workout plan')}. "
            f"Estimated goal period is about {eta} weeks. {_format_today_workout(workout_plan)}"
        )
    elif topic == 'progress':
        reply = (
            f"{bmi_text}Today you've eaten about {today.get('calories_in', 0)} kcal and burned about {today.get('calories_out', 0)} kcal. "
            f"You are targeting roughly {daily_calories} kcal/day, and you've trained {context.get('week', {}).get('workout_count', 0)} time(s) in the last 7 days."
        )
    elif topic == 'hydration':
        reply = (
            f"You've logged {today.get('water_ml', 0)} ml of water today. "
            "A practical target is 2500-3000 ml per day, and a simple win is 500 ml after waking, 500 ml around training, and steady sipping with meals."
        )
    elif topic == 'recovery':
        reply = (
            f"You've logged {today.get('sleep_hours', 0)} hours of sleep today. "
            "For better recovery and body composition, aim for 7-8 hours, keep one lighter recovery day each week, and don’t stack hard sessions when sleep is poor."
        )
    elif topic == 'body_metrics':
        reply = (
            f"{bmi_text}{body_fat_text}"
            f"Your plan is tuned for {profile.fitness_goal.replace('_', ' ')}, and the app currently estimates about {workout_plan.get('goal_eta_weeks', 'N/A')} weeks to move toward your next milestone."
        )
    else:
        reply = (
            f"{bmi_text}{body_fat_text}Your current target is about {daily_calories} kcal/day. "
            f"Today’s workout focus is {workout_plan.get('today_plan', {}).get('plan_name', 'not loaded yet')}. "
            "Ask me for breakfast, workout, calories left, hydration, sleep, or progress and I’ll answer from your live app data."
        )

    return _build_response(reply, provider, topic)


def _build_response(reply: str, provider: str, topic: str):
    return jsonify({
        "status": "success",
        "reply": reply,
        "speak": True,
        "provider": provider,
        "topic": topic,
        "suggestions": TOPIC_SUGGESTIONS.get(topic, TOPIC_SUGGESTIONS['general'])
    }), 200
