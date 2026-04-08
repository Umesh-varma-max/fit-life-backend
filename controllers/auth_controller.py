# controllers/auth_controller.py
from flask import jsonify
from extensions import db, bcrypt
from flask_jwt_extended import create_access_token
from models.user import User
from utils.validators import normalize_email


def register_user(data: dict):
    """Create a new user account."""
    email = normalize_email(data['email'])

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email already registered"}), 400

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        full_name=data['full_name'].strip(),
        email=email,
        password_hash=hashed
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User registered successfully",
        "user_id": user.id
    }), 201


def login_user(data: dict):
    """Authenticate user and return JWT."""
    email = normalize_email(data['email'])
    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    # Flask-JWT-Extended stores the identity in the JWT subject claim.
    # Using a string here avoids follow-up auth failures in newer JWT stacks.
    token = create_access_token(identity=str(user.id))
    return jsonify({
        "status": "success",
        "access_token": token,
        "user": user.to_dict()
    }), 200
