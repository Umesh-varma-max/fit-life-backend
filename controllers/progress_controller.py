# controllers/progress_controller.py
from flask import jsonify
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from utils.bmi_calculator import calculate_bmi
from datetime import date, timedelta
from sqlalchemy import func


def get_progress(user_id: int, period: str = 'weekly'):
    """Return progress data for charts (weekly or monthly)."""
    today = date.today()

    if period == 'monthly':
        start_date = today - timedelta(days=30)
    else:
        start_date = today - timedelta(days=7)

    # Get logs for the period
    logs = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.log_date >= start_date,
        ActivityLog.log_date <= today
    ).all()

    # Average calories
    days_count = max((today - start_date).days, 1)
    total_cal_in  = sum(l.calories_in or 0 for l in logs)
    total_cal_out = sum(l.calories_out or 0 for l in logs)

    # Workout days count
    workout_dates = set(l.log_date for l in logs if l.log_type == 'workout')

    # Weight history (from profile — single point for now)
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    weight_history = []
    bmi_trend = []

    if profile:
        weight_history.append({
            "date": str(today),
            "weight_kg": float(profile.weight_kg) if profile.weight_kg else None
        })
        if profile.bmi:
            bmi_trend.append(float(profile.bmi))

    return jsonify({
        "status": "success",
        "period": period,
        "weight_history": weight_history,
        "avg_calories_in": int(total_cal_in / days_count),
        "avg_calories_out": int(total_cal_out / days_count),
        "workout_days": len(workout_dates),
        "bmi_trend": bmi_trend
    }), 200
