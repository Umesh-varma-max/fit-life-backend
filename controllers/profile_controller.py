# controllers/profile_controller.py
from flask import jsonify
from extensions import db
from models.health_profile import HealthProfile
from models.recommendation import Recommendation
from utils.bmi_calculator import (
    calculate_bmi, calculate_bmr, calculate_tdee, calculate_daily_calories
)
from utils.recommendation_engine import generate_recommendation


def get_profile(user_id: int):
    """Return user's health profile."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"status": "error", "message": "Profile not found"}), 404
    return jsonify({"status": "success", "profile": profile.to_dict()}), 200


def save_profile(user_id: int, data: dict):
    """Create or update health profile. Auto-calculates BMI, BMR, TDEE."""
    # Calculate health metrics
    bmi  = calculate_bmi(data['weight_kg'], data['height_cm'])
    bmr  = calculate_bmr(data['weight_kg'], data['height_cm'], data['age'], data['gender'])
    tdee = calculate_tdee(bmr, data['activity_level'])
    cal  = calculate_daily_calories(tdee, data['fitness_goal'])

    profile = HealthProfile.query.filter_by(user_id=user_id).first()

    if profile:
        # Update existing profile
        for key, val in data.items():
            setattr(profile, key, val)
        profile.bmi = bmi
        profile.bmr = bmr
        profile.daily_calories = cal
    else:
        # Create new profile
        profile = HealthProfile(
            user_id=user_id,
            bmi=bmi,
            bmr=bmr,
            daily_calories=cal,
            **data
        )
        db.session.add(profile)

    db.session.commit()

    # Auto-regenerate recommendations after profile save
    _refresh_recommendations(user_id, profile)

    return jsonify({
        "status": "success",
        "message": "Profile saved",
        "bmi": bmi,
        "bmr": bmr,
        "daily_calories": cal
    }), 200


def _refresh_recommendations(user_id: int, profile):
    """Internal: regenerates and saves recommendation after profile change."""
    rec_data = generate_recommendation(profile)
    rec = Recommendation.query.filter_by(user_id=user_id).first()
    if rec:
        for k, v in rec_data.items():
            setattr(rec, k, v)
    else:
        rec = Recommendation(user_id=user_id, **rec_data)
        db.session.add(rec)
    db.session.commit()
