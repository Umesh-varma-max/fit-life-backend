# routes/ai_routes.py
from flask import Blueprint, request, jsonify
from extensions import limiter
from middleware.auth_middleware import jwt_required_custom
from controllers.ai_controller import diet_chat

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')


@ai_bp.route('/diet-chat', methods=['POST'])
@jwt_required_custom
@limiter.limit("60 per hour")
def chat(current_user):
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({"status": "error", "message": "Message is required"}), 400
    return diet_chat(current_user.id, message)
