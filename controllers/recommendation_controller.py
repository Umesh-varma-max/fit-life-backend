from flask import jsonify

from extensions import db
from models.health_profile import HealthProfile
from models.recommendation import Recommendation
from utils.recommendation_engine import generate_recommendation
from utils.workout_planner import generate_profile_workout_plan


def _legacy_workout_map(detailed_plan: dict) -> dict:
    """Return the simple day->exercise map expected by the current frontend."""
    return {
        day['day']: [
            {
                'name': exercise.get('name'),
                'sets': exercise.get('sets', 0),
                'reps': exercise.get('reps', 0),
                'duration_min': exercise.get('estimated_duration_min') or exercise.get('duration_min', 0)
            }
            for exercise in day.get('exercises', [])
        ]
        for day in detailed_plan.get('days', [])
    }


def _upsert_recommendation(user_id: int, rec_data: dict):
    rec = Recommendation.query.filter_by(user_id=user_id).first()
    if rec:
        for key, value in rec_data.items():
            setattr(rec, key, value)
    else:
        rec = Recommendation(user_id=user_id, **rec_data)
        db.session.add(rec)
    db.session.commit()
    return rec


def get_recommendation(user_id: int):
    """Return fresh recommendation data based on the latest profile."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()

    if not profile:
        return jsonify({
            "status": "error",
            "message": "Please create your health profile first"
        }), 404

    rec_data = generate_recommendation(profile)
    rec = _upsert_recommendation(user_id, rec_data)

    recommendation_payload = rec.to_dict()
    detailed_workout_plan = generate_profile_workout_plan(profile)
    recommendation_payload['workout_plan'] = _legacy_workout_map(detailed_workout_plan)
    recommendation_payload['workout_plan_details'] = detailed_workout_plan
    recommendation_payload['goal_eta_weeks'] = detailed_workout_plan.get('goal_eta_weeks')
    recommendation_payload['goal_label'] = detailed_workout_plan.get('goal_label')
    recommendation_payload['goal_badge'] = detailed_workout_plan.get('goal_badge')
    recommendation_payload['hero_image_url'] = detailed_workout_plan.get('hero_image_url')
    recommendation_payload['body_fat_category'] = getattr(profile, 'body_fat_category', None)

    return jsonify({
        "status": "success",
        "recommendations": recommendation_payload
    }), 200
