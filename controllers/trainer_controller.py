# controllers/trainer_controller.py
from flask import jsonify
from models.trainer import Trainer


def list_trainers(location: str = None):
    """List trainers, optionally filtered by location."""
    query = Trainer.query.filter_by(available=True)

    if location and location.strip():
        query = query.filter(Trainer.location.ilike(f'%{location.strip()}%'))

    trainers = query.order_by(Trainer.rating.desc()).all()

    return jsonify({
        "status": "success",
        "trainers": [t.to_dict() for t in trainers]
    }), 200
