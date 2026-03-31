# routes/__init__.py

def register_blueprints(app):
    """Register all route blueprints with the Flask app."""
    from routes.auth_routes import auth_bp
    from routes.profile_routes import profile_bp
    from routes.recommendation_routes import recommend_bp
    from routes.activity_routes import activity_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.food_routes import food_bp
    from routes.workout_routes import workout_bp
    from routes.trainer_routes import trainer_bp
    from routes.doctor_routes import doctor_bp
    from routes.ai_routes import ai_bp
    from routes.reminder_routes import reminder_bp
    from routes.progress_routes import progress_bp
    from routes.export_routes import export_bp

    blueprints = [
        auth_bp, profile_bp, recommend_bp, activity_bp,
        dashboard_bp, food_bp, workout_bp, trainer_bp,
        doctor_bp, ai_bp, reminder_bp, progress_bp, export_bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)
