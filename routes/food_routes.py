# routes/food_routes.py
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import jwt_required_custom
from controllers.food_controller import search_food, analyze_food_name, analyze_food_photo

food_bp = Blueprint('food', __name__, url_prefix='/api/food')


@food_bp.route('/search', methods=['GET'])
@jwt_required_custom
def food_search(current_user):
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"status": "error", "message": "Search query 'q' is required"}), 400
    return search_food(query)


@food_bp.route('/scan', methods=['POST'])
@jwt_required_custom
def food_scan(current_user):
    data = request.get_json(silent=True) or {}
    food_name = data.get('food_name', '').strip()
    if not food_name:
        return jsonify({"status": "error", "message": "food_name is required"}), 400

    response_payload, status_code = analyze_food_name(
        food_name=food_name or None,
        quantity_g=data.get('quantity_g', 100),
        meal_time=data.get('meal_time'),
        should_log=bool(data.get('log_meal') or data.get('mark_as_eaten') or data.get('auto_log')),
        log_date=data.get('log_date'),
        user_id=current_user.id
    )
    return jsonify(response_payload), status_code


@food_bp.route('/analyze-photo', methods=['POST'])
@jwt_required_custom
def food_photo_analyze(current_user):
    image_file = request.files.get('photo')
    if not image_file:
        return jsonify({"status": "error", "message": "photo file is required"}), 400

    image_bytes = image_file.read()
    if not image_bytes:
        return jsonify({"status": "error", "message": "Uploaded photo is empty"}), 400

    response_payload, status_code = analyze_food_photo(
        image_bytes=image_bytes,
        mime_type=image_file.mimetype or 'image/jpeg',
        filename=image_file.filename,
        meal_time=request.form.get('meal_time'),
        should_log=request.form.get('log_meal', '').lower() in {'1', 'true', 'yes', 'on'},
        log_date=request.form.get('log_date'),
        user_id=current_user.id
    )
    return jsonify(response_payload), status_code
