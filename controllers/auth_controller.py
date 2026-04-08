from datetime import datetime

from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity
)

from extensions import bcrypt, db
from models.user import User
from utils.validators import normalize_email


def _build_auth_payload(user: User) -> dict:
    additional_claims = {
        "token_version": int(user.token_version or 0),
        "role": user.role
    }
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)
    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }


def register_user(data: dict):
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
    email = normalize_email(data['email'])
    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    user.last_login_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_build_auth_payload(user)), 200


def refresh_session():
    user_id = int(get_jwt_identity())
    token_version = int((get_jwt() or {}).get('token_version', -1))
    user = User.query.get(user_id)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 401
    if int(user.token_version or 0) != token_version:
        return jsonify({"status": "error", "message": "Session expired. Please log in again."}), 401

    return jsonify(_build_auth_payload(user)), 200


def logout_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 401

    user.token_version = int(user.token_version or 0) + 1
    db.session.commit()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200


def get_current_user(user: User):
    profile = user.profile.to_dict() if user.profile else None
    return jsonify({
        "status": "success",
        "user": user.to_dict(),
        "profile": profile
    }), 200
