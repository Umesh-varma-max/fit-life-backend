# app.py
"""
FitLife Backend — Entry Point
Flask application factory with all extensions, blueprints, and error handlers.
"""

import os
from flask import Flask, jsonify
from extensions import db, jwt, bcrypt, cors, migrate, limiter, scheduler
from config import config_map
from routes import register_blueprints


def create_app(config_name=None):
    """
    Application factory.
    Creates and configures the Flask app.
    """
    app = Flask(__name__)

    # Load config
    env = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(env, config_map['development']))

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS: allow requests from frontend origin
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['FRONTEND_ORIGIN'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register all route blueprints
    register_blueprints(app)

    # Import all models so Flask-Migrate discovers them
    with app.app_context():
        import models  # noqa: F401

    # ─── Global Error Handlers ────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"status": "error", "message": "Method not allowed"}), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"status": "error", "message": "Rate limit exceeded. Please try again later."}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    # ─── Health Check ─────────────────────────────────────

    @app.route('/health')
    def health():
        return jsonify({"status": "ok", "version": "1.0.0"})

    # ─── Start Background Scheduler ──────────────────────

    if not scheduler.running:
        try:
            scheduler.start()
        except Exception:
            pass  # Scheduler may already be running in debug mode (reloader)

    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
