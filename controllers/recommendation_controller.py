# controllers/recommendation_controller.py
from flask import jsonify
from models.recommendation import Recommendation
from models.health_profile import HealthProfile
from utils.recommendation_engine import generate_recommendation
from utils.workout_templates import build_goal_based_workout_plan
from extensions import db


def get_recommendation(user_id: int):
    """Return cached recommendation, or generate if missing."""
    rec = Recommendation.query.filter_by(user_id=user_id).first()
    profile = HealthProfile.query.filter_by(user_id=user_id).first()

    if not rec:
        # Try to generate from profile
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
    if profile:
        recommendation_payload['workout_plan'] = build_goal_based_workout_plan(profile.fitness_goal)

    return jsonify({
        "status": "success",
        "recommendations": recommendation_payload
    }), 200
