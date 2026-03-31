# controllers/reminder_controller.py
from flask import jsonify
from extensions import db
from models.reminder import Reminder
from utils.validators import parse_time_string


def list_reminders(user_id: int):
    """Return all reminders for the user."""
    reminders = Reminder.query.filter_by(user_id=user_id).order_by(Reminder.remind_at).all()
    return jsonify({
        "status": "success",
        "reminders": [r.to_dict() for r in reminders]
    }), 200


def add_reminder(user_id: int, data: dict):
    """Create a new reminder."""
    try:
        remind_time = parse_time_string(data['remind_at'])
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    reminder = Reminder(
        user_id=user_id,
        reminder_type=data['reminder_type'],
        message=data['message'],
        remind_at=remind_time,
        repeat_daily=data.get('repeat_daily', True),
        is_active=True
    )
    db.session.add(reminder)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Reminder created",
        "reminder_id": reminder.id
    }), 201


def delete_reminder(user_id: int, reminder_id: int):
    """Delete a reminder (with ownership verification)."""
    reminder = Reminder.query.filter_by(id=reminder_id, user_id=user_id).first()

    if not reminder:
        return jsonify({"status": "error", "message": "Reminder not found"}), 404

    db.session.delete(reminder)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Reminder deleted"
    }), 200
