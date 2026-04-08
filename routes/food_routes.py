# routes/food_routes.py
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import jwt_required_custom
from controllers.food_controller import (
    analyze_food_photo,
    finalize_food_log,
    scan_food,
    search_food
)

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
    barcode = data.get('barcode', '').strip()
    food_name = data.get('food_name', '').strip()
    if not barcode and not food_name:
        return jsonify({"status": "error", "message": "Either barcode or food_name is required"}), 400

    response_payload, status_code = scan_food(
        barcode=barcode or None,
        food_name=food_name or None,
        quantity_g=data.get('quantity_g', 100),
        meal_time=data.get('meal_time'),
        should_log=bool(data.get('log_meal') or data.get('mark_as_eaten') or data.get('auto_log')),
        log_date=data.get('log_date'),
        current_user=current_user
    )
    if status_code != 200:
        return jsonify(response_payload), status_code
    return finalize_food_log(current_user.id, response_payload)


@food_bp.route('/analyze-photo', methods=['POST'])
@jwt_required_custom
def food_analyze_photo(current_user):
    photo = request.files.get('photo')
    if not photo:
        return jsonify({"status": "error", "message": "Photo file is required"}), 400

    response_payload, status_code = analyze_food_photo(
        photo,
        food_hint=request.form.get('food_hint', '').strip(),
        current_user=current_user,
        meal_time=request.form.get('meal_time'),
        should_log=bool(
            request.form.get('log_meal')
            or request.form.get('mark_as_eaten')
            or request.form.get('auto_log')
        ),
        log_date=request.form.get('log_date')
    )
    if status_code != 200:
        return jsonify(response_payload), status_code
    return finalize_food_log(current_user.id, response_payload)
