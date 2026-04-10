# controllers/activity_controller.py
from io import BytesIO

from flask import jsonify, send_file
from extensions import db
from models.activity_log import ActivityLog
from datetime import date


def log_activity(user_id: int, data: dict):
    """Create a new activity log entry (meal, workout, water, or sleep)."""
    log = ActivityLog(
        user_id=user_id,
        log_date=data.get('log_date') or date.today(),
        log_type=data['log_type'],
        description=data.get('description'),
        calories_in=data.get('calories_in', 0),
        calories_out=data.get('calories_out', 0),
        water_ml=data.get('water_ml', 0),
        sleep_hours=data.get('sleep_hours', 0),
        duration_min=data.get('duration_min', 0)
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Activity logged",
        "log_id": log.id
    }), 201


def get_activity(user_id: int, log_date=None):
    """Get all activity logs for a specific date with daily summary."""
    if log_date is None:
        log_date = date.today()

    logs = ActivityLog.query.filter_by(
        user_id=user_id, log_date=log_date
    ).order_by(ActivityLog.created_at.desc()).all()

    # Calculate daily summary
    cal_in    = sum(l.calories_in or 0 for l in logs)
    cal_out   = sum(l.calories_out or 0 for l in logs)
    water     = sum(l.water_ml or 0 for l in logs)
    sleep_hrs = sum(float(l.sleep_hours or 0) for l in logs)

    return jsonify({
        "status": "success",
        "date": str(log_date),
        "summary": {
            "calories_in": cal_in,
            "calories_out": cal_out,
            "net_calories": cal_in - cal_out,
            "water_ml": water,
            "sleep_hours": round(sleep_hrs, 1)
        },
        "logs": [l.to_dict() for l in logs]
    }), 200


def get_activity_image(user_id: int, log_id: int):
    """Return a persisted scan image for a meal/activity log."""
    log = ActivityLog.query.filter_by(id=log_id, user_id=user_id).first()
    if not log:
        return jsonify({"status": "error", "message": "Activity log not found"}), 404
    if not log.image_blob or not log.image_mime_type:
        return jsonify({"status": "error", "message": "No image stored for this log"}), 404

    download_name = log.image_filename or f"scan-{log.id}.jpg"
    return send_file(
        BytesIO(log.image_blob),
        mimetype=log.image_mime_type,
        download_name=download_name,
        as_attachment=False,
        max_age=86400
    )
