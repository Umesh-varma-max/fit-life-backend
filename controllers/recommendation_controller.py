from flask import jsonify

from extensions import db
from models.health_profile import HealthProfile
from models.recommendation import Recommendation
from utils.ai_structured import groq_json_completion
from utils.goal_presets import goal_label, normalize_goal
from utils.recommendation_engine import generate_recommendation
from utils.workout_templates import build_goal_based_workout_plan


def _recommendation_prompt(goal: str, prompt_text: str = None) -> str:
    default_prompt = (
        f"Generate a weekly fitness recommendation for the goal '{goal_label(goal)}'. "
        "Return pure JSON only with this exact structure: "
        "{\"goal_label\": string, \"weekly_workout_plan\": [{\"day\": string, \"focus_area\": string, "
        "\"exercises\": [string]}], \"nutrition_tips\": [string], \"motivational_tip\": string}. "
        "Keep it practical and app-friendly."
    )
    return prompt_text.strip() if prompt_text else default_prompt


def _fallback_recommendation(goal: str, profile) -> dict:
    rec_data = generate_recommendation(profile) if profile else {
        "daily_calories": 2200,
        "diet_plan": {},
        "weekly_tips": [
            "Stay consistent with meals and training.",
            "Hydrate well and keep sleep on schedule."
        ],
        "bmi_category": "Unknown"
    }
    workout_plan = build_goal_based_workout_plan(goal)
    weekly_workout_plan = [
        {
            "day": day["day"],
            "focus_area": day.get("focus_area", "Workout"),
            "exercises": [exercise["name"] for exercise in day["exercises"]]
        }
        for day in workout_plan["days"]
    ]
    return {
        "goal_label": goal_label(goal),
        "weekly_workout_plan": weekly_workout_plan,
        "nutrition_tips": rec_data.get("weekly_tips", [])[:4],
        "motivational_tip": (rec_data.get("weekly_tips") or ["Consistency compounds over time."])[0],
        "daily_calories": rec_data.get("daily_calories"),
        "diet_plan": rec_data.get("diet_plan", {})
    }


def generate_recommendation_payload(user_id: int, goal: str = None, prompt_text: str = None):
    """Generate structured recommendation cards for the selected goal."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    canonical_goal = normalize_goal(goal or (profile.fitness_goal if profile else None))

    try:
        ai_payload = groq_json_completion(
            system_prompt=(
                "You generate structured workout and nutrition guidance for FitLife. "
                "Return JSON only. No markdown."
            ),
            user_prompt=_recommendation_prompt(canonical_goal, prompt_text)
        )
        payload = {
            "goal": canonical_goal,
            "goal_label": ai_payload.get("goal_label") or goal_label(canonical_goal),
            "weekly_workout_plan": ai_payload.get("weekly_workout_plan", []),
            "nutrition_tips": ai_payload.get("nutrition_tips", []),
            "motivational_tip": ai_payload.get("motivational_tip", "Stay consistent and trust the process."),
            "prompt_used": _recommendation_prompt(canonical_goal, prompt_text),
            "source": "ai"
        }
    except Exception:
        fallback = _fallback_recommendation(canonical_goal, profile)
        payload = {
            "goal": canonical_goal,
            **fallback,
            "prompt_used": _recommendation_prompt(canonical_goal, prompt_text),
            "source": "fallback_template"
        }

    return jsonify({"status": "success", "recommendations": payload}), 200


def get_recommendation(user_id: int, goal: str = None):
    """Return cached recommendation, or generate if missing, then enrich for the frontend."""
    rec = Recommendation.query.filter_by(user_id=user_id).first()
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    canonical_goal = normalize_goal(goal or (profile.fitness_goal if profile else None))

    if not rec:
        if not profile:
            return jsonify({
                "status": "error",
                "message": "Please create your health profile first"
            }), 404

        rec_data = generate_recommendation(profile)
        rec = Recommendation(user_id=user_id, **rec_data)
        db.session.add(rec)
        db.session.commit()

    recommendation_payload = rec.to_dict()
    recommendation_payload['goal'] = canonical_goal
    recommendation_payload['goal_label'] = goal_label(canonical_goal)
    recommendation_payload['workout_plan'] = build_goal_based_workout_plan(canonical_goal)
    recommendation_payload['weekly_workout_plan'] = [
        {
            "day": day["day"],
            "focus_area": day.get("focus_area", "Workout"),
            "exercises": [exercise["name"] for exercise in day["exercises"]]
        }
        for day in recommendation_payload['workout_plan']["days"]
    ]
    recommendation_payload['nutrition_tips'] = recommendation_payload.get('weekly_tips', [])
    recommendation_payload['motivational_tip'] = (
        recommendation_payload['weekly_tips'][0]
        if recommendation_payload.get('weekly_tips')
        else "Stay consistent and trust the process."
    )

    return jsonify({
        "status": "success",
        "recommendations": recommendation_payload
    }), 200
