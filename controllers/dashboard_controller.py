# controllers/dashboard_controller.py
from flask import jsonify
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.recommendation import Recommendation
from utils.quote_generator import get_daily_quote
from datetime import date, timedelta


def get_dashboard(user_id: int):
    """Aggregate dashboard data: today's stats, weekly chart, streak, quote."""
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    rec     = Recommendation.query.filter_by(user_id=user_id).first()
    today   = date.today()

    # Today's totals
    today_logs = ActivityLog.query.filter_by(user_id=user_id, log_date=today).all()
    cal_in  = sum(l.calories_in or 0 for l in today_logs)
    cal_out = sum(l.calories_out or 0 for l in today_logs)
    water   = sum(l.water_ml or 0 for l in today_logs)

    # Weekly chart data (last 7 days)
    week_labels, week_in, week_out = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_logs = ActivityLog.query.filter_by(user_id=user_id, log_date=d).all()
        week_labels.append(d.strftime('%a'))
        week_in.append(sum(l.calories_in or 0 for l in day_logs))
        week_out.append(sum(l.calories_out or 0 for l in day_logs))

    # Workout streak (consecutive days with at least 1 workout)
    streak = _calculate_streak(user_id, today)

    # Goal progress percentage
    daily_goal = profile.daily_calories if profile else 2000
    pct = min(int((cal_in / daily_goal) * 100), 100) if daily_goal else 0

    return jsonify({
        "status": "success",
        "dashboard": {
            "bmi":                float(profile.bmi) if profile and profile.bmi else None,
            "bmi_category":       rec.bmi_category if rec else "—",
            "today_calories_in":  cal_in,
            "today_calories_out": cal_out,
            "daily_calorie_goal": daily_goal,
            "goal_progress_pct":  pct,
            "workout_streak":     streak,
            "water_today_ml":     water,
            "water_goal_ml":      3000,
            "weekly_chart": {
                "labels":       week_labels,
                "calories_in":  week_in,
                "calories_out": week_out
            },
            "motivational_quote": get_daily_quote(),
            "this_week_tip":      (rec.weekly_tips[0] if rec and rec.weekly_tips else "Stay consistent!")
        }
    }), 200


def _calculate_streak(user_id: int, today: date) -> int:
    """Count consecutive days with at least one workout logged."""
    streak = 0
    d = today
    while True:
        workouts = ActivityLog.query.filter_by(
            user_id=user_id, log_date=d, log_type='workout'
        ).count()
        if workouts == 0:
            break
        streak += 1
        d -= timedelta(days=1)
    return streak
