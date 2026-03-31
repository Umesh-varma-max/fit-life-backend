# controllers/doctor_controller.py
from flask import jsonify
from models.doctor import Doctor


def list_doctors(specialization: str = None):
    """List doctors, optionally filtered by specialization."""
    query = Doctor.query

    if specialization and specialization.strip():
        query = query.filter(Doctor.specialization.ilike(f'%{specialization.strip()}%'))

    doctors = query.order_by(Doctor.rating.desc()).all()

    return jsonify({
        "status": "success",
        "doctors": [d.to_dict() for d in doctors]
    }), 200
