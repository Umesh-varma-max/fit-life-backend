# ⚙️ BACKEND PLAN — AI Fitness Management System
## Standalone Repo · Python Flask · MySQL · JWT · REST API

> **Repo Name:** `fitness-backend`  
> **Language:** Python 3.11+  
> **Framework:** Flask  
> **Database:** MySQL 8.0  
> **Auth:** JWT (Flask-JWT-Extended)  
> **ORM:** SQLAlchemy + Flask-Migrate  
> **API Style:** REST  
> **CORS:** Enabled for all `http://localhost:3000` (dev) and your frontend domain (prod)

---

# TABLE OF CONTENTS

1. [Repo Structure](#1-repo-structure)
2. [Environment Setup (.env)](#2-environment-setup-env)
3. [requirements.txt](#3-requirementstxt)
4. [Database Schema (MySQL)](#4-database-schema-mysql)
5. [extensions.py — Shared Instances](#5-extensionspy--shared-instances)
6. [config.py](#6-configpy)
7. [app.py — App Factory](#7-apppy--app-factory)
8. [Models (SQLAlchemy)](#8-models-sqlalchemy)
9. [Schemas (Marshmallow Validation)](#9-schemas-marshmallow-validation)
10. [Middleware](#10-middleware)
11. [Utils](#11-utils)
12. [Controllers](#12-controllers)
13. [Routes (Blueprints)](#13-routes-blueprints)
14. [API Contract (Backend Side)](#14-api-contract-backend-side)
15. [AI Integration (Claude API)](#15-ai-integration-claude-api)
16. [PDF Export](#16-pdf-export)
17. [Scheduler — Daily Reminders](#17-scheduler--daily-reminders)
18. [Security Checklist](#18-security-checklist)
19. [Setup & Run Instructions](#19-setup--run-instructions)
20. [Deployment Notes](#20-deployment-notes)

---

# 1. REPO STRUCTURE

```
fitness-backend/
│
├── app.py                          # Entry point — creates and runs Flask app
├── config.py                       # DevelopmentConfig / ProductionConfig
├── extensions.py                   # db, jwt, bcrypt, cors, migrate, limiter, scheduler
├── requirements.txt
├── .env                            # Secret keys (never commit)
├── .env.example                    # Safe template to commit
├── .gitignore
├── README.md
│
├── models/
│   ├── __init__.py                 # Import all models here
│   ├── user.py                     # User model
│   ├── health_profile.py           # HealthProfile model
│   ├── activity_log.py             # ActivityLog model
│   ├── recommendation.py           # Recommendation model
│   ├── food_item.py                # FoodItem model
│   ├── workout_plan.py             # WorkoutPlan model
│   ├── trainer.py                  # Trainer model
│   ├── doctor.py                   # Doctor model
│   └── reminder.py                 # Reminder model
│
├── schemas/
│   ├── __init__.py
│   ├── auth_schema.py              # RegisterSchema, LoginSchema
│   ├── profile_schema.py           # HealthProfileSchema
│   ├── activity_schema.py          # ActivityLogSchema
│   ├── workout_schema.py           # WorkoutPlanSchema
│   └── reminder_schema.py          # ReminderSchema
│
├── middleware/
│   ├── __init__.py
│   ├── auth_middleware.py          # JWT verification helpers
│   └── validation_middleware.py    # Input sanitization helpers
│
├── controllers/
│   ├── __init__.py
│   ├── auth_controller.py          # register, login, logout
│   ├── profile_controller.py       # get_profile, save_profile, calc_bmi_bmr
│   ├── recommendation_controller.py# generate_recommendations
│   ├── activity_controller.py      # log_activity, get_activity
│   ├── dashboard_controller.py     # get_dashboard_summary
│   ├── food_controller.py          # search_food, scan_barcode
│   ├── workout_controller.py       # get_plan, save_plan, log_timer
│   ├── trainer_controller.py       # list_trainers
│   ├── doctor_controller.py        # list_doctors
│   ├── ai_controller.py            # diet_chat (Claude API)
│   ├── reminder_controller.py      # list, add, delete reminders
│   ├── progress_controller.py      # get_progress (weekly/monthly)
│   └── export_controller.py        # generate_pdf_report
│
├── routes/
│   ├── __init__.py                 # register_blueprints(app)
│   ├── auth_routes.py              # Blueprint: auth_bp
│   ├── profile_routes.py           # Blueprint: profile_bp
│   ├── recommendation_routes.py    # Blueprint: recommend_bp
│   ├── activity_routes.py          # Blueprint: activity_bp
│   ├── dashboard_routes.py         # Blueprint: dashboard_bp
│   ├── food_routes.py              # Blueprint: food_bp
│   ├── workout_routes.py           # Blueprint: workout_bp
│   ├── trainer_routes.py           # Blueprint: trainer_bp
│   ├── doctor_routes.py            # Blueprint: doctor_bp
│   ├── ai_routes.py                # Blueprint: ai_bp
│   ├── reminder_routes.py          # Blueprint: reminder_bp
│   ├── progress_routes.py          # Blueprint: progress_bp
│   └── export_routes.py            # Blueprint: export_bp
│
└── utils/
    ├── __init__.py
    ├── bmi_calculator.py           # BMI, BMR, TDEE formulas
    ├── recommendation_engine.py    # Rule-based diet + workout logic
    ├── diet_templates.py           # Diet plans per goal + food preference
    ├── workout_templates.py        # Workout plans per goal
    ├── quote_generator.py          # Daily motivational quotes
    ├── pdf_generator.py            # WeasyPrint PDF builder
    └── validators.py               # Custom validation helpers
```

---

# 2. ENVIRONMENT SETUP (.env)

```bash
# .env — DO NOT COMMIT THIS FILE

# Flask
SECRET_KEY=your-flask-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1

# JWT
JWT_SECRET_KEY=your-jwt-secret-key-here

# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fitness_db
DB_USER=root
DB_PASSWORD=your_mysql_password

# Anthropic Claude API (for AI diet planner)
ANTHROPIC_API_KEY=sk-ant-...

# CORS
FRONTEND_ORIGIN=http://localhost:3000
```

```bash
# .env.example — COMMIT THIS (no real secrets)
SECRET_KEY=change-this-in-production
JWT_SECRET_KEY=change-this-jwt-secret
DB_HOST=localhost
DB_PORT=3306
DB_NAME=fitness_db
DB_USER=root
DB_PASSWORD=yourpassword
ANTHROPIC_API_KEY=sk-ant-REPLACE_ME
FRONTEND_ORIGIN=http://localhost:3000
```

---

# 3. REQUIREMENTS.TXT

```
# Core Framework
Flask==3.0.2
Werkzeug==3.0.1

# Database
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
PyMySQL==1.1.0
cryptography==42.0.5

# Auth
Flask-JWT-Extended==4.6.0
Flask-Bcrypt==1.0.1

# Validation
marshmallow==3.21.1
Flask-Marshmallow==1.2.0

# CORS
Flask-CORS==4.0.0

# Rate Limiting
Flask-Limiter==3.5.0

# AI (Claude)
anthropic==0.23.0

# HTTP
requests==2.31.0

# PDF Generation
WeasyPrint==60.2

# Scheduler (reminders)
APScheduler==3.10.4

# Environment
python-dotenv==1.0.1

# Development only
pytest==8.1.1
pytest-flask==1.3.0
```

---

# 4. DATABASE SCHEMA (MySQL)

Run this SQL to initialize the database:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS fitness_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fitness_db;

-- ─── USERS ───────────────────────────────────────────────────────
CREATE TABLE users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(100)        NOT NULL,
    email           VARCHAR(150)        UNIQUE NOT NULL,
    password_hash   VARCHAR(255)        NOT NULL,
    role            ENUM('user','admin') DEFAULT 'user',
    created_at      TIMESTAMP           DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP           DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email)
);

-- ─── HEALTH PROFILES ─────────────────────────────────────────────
CREATE TABLE health_profiles (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL UNIQUE,
    age             INT             NOT NULL,
    gender          ENUM('male','female','other') NOT NULL,
    height_cm       DECIMAL(5,2)    NOT NULL,
    weight_kg       DECIMAL(5,2)    NOT NULL,
    activity_level  ENUM('sedentary','light','moderate','active') NOT NULL,
    sleep_hours     DECIMAL(4,2)    DEFAULT 7.0,
    food_habits     ENUM('veg','non-veg','vegan','keto','paleo') DEFAULT 'non-veg',
    fitness_goal    ENUM('weight_loss','muscle_gain','maintenance') NOT NULL,
    bmi             DECIMAL(5,2),
    bmr             DECIMAL(8,2),
    daily_calories  INT,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_profile (user_id)
);

-- ─── ACTIVITY LOGS ────────────────────────────────────────────────
CREATE TABLE activity_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    log_date        DATE            NOT NULL,
    log_type        ENUM('meal','workout','water','sleep') NOT NULL,
    description     VARCHAR(255),
    calories_in     INT             DEFAULT 0,
    calories_out    INT             DEFAULT 0,
    water_ml        INT             DEFAULT 0,
    sleep_hours     DECIMAL(4,2)    DEFAULT 0,
    duration_min    INT             DEFAULT 0,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, log_date)
);

-- ─── RECOMMENDATIONS ──────────────────────────────────────────────
CREATE TABLE recommendations (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    diet_plan       JSON,
    workout_plan    JSON,
    daily_calories  INT,
    weekly_tips     JSON,
    bmi_category    VARCHAR(50),
    generated_at    TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_rec (user_id)
);

-- ─── FOOD ITEMS ───────────────────────────────────────────────────
CREATE TABLE food_items (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    name                VARCHAR(150)    NOT NULL,
    calories_per_100g   DECIMAL(7,2),
    protein_g           DECIMAL(6,2),
    carbs_g             DECIMAL(6,2),
    fat_g               DECIMAL(6,2),
    fiber_g             DECIMAL(6,2),
    barcode             VARCHAR(50),
    source              VARCHAR(50)     DEFAULT 'manual',
    INDEX idx_name (name),
    INDEX idx_barcode (barcode)
);

-- ─── WORKOUT PLANS ────────────────────────────────────────────────
CREATE TABLE workout_plans (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    plan_name       VARCHAR(100),
    day_of_week     ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun'),
    exercises       JSON,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_workout (user_id)
);

-- ─── TRAINERS ─────────────────────────────────────────────────────
CREATE TABLE trainers (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    specialization  VARCHAR(150),
    location        VARCHAR(200),
    contact_email   VARCHAR(150),
    contact_phone   VARCHAR(20),
    rating          DECIMAL(3,2)    DEFAULT 0.0,
    available       BOOLEAN         DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ─── DOCTORS ──────────────────────────────────────────────────────
CREATE TABLE doctors (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    specialization  VARCHAR(150),
    hospital        VARCHAR(200),
    contact_email   VARCHAR(150),
    contact_phone   VARCHAR(20),
    available_slots JSON,
    rating          DECIMAL(3,2)    DEFAULT 0.0,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

-- ─── REMINDERS ────────────────────────────────────────────────────
CREATE TABLE reminders (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT             NOT NULL,
    reminder_type   ENUM('workout','meal','water','sleep','custom') NOT NULL,
    message         TEXT,
    remind_at       TIME,
    repeat_daily    BOOLEAN         DEFAULT TRUE,
    is_active       BOOLEAN         DEFAULT TRUE,
    created_at      TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_reminder (user_id)
);
```

---

# 5. EXTENSIONS.PY — SHARED INSTANCES

```python
# extensions.py
# All Flask extensions initialized here (without app).
# app factory pattern: avoids circular imports.

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler

db        = SQLAlchemy()
jwt       = JWTManager()
bcrypt    = Bcrypt()
cors      = CORS()
migrate   = Migrate()
scheduler = BackgroundScheduler()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"]
)
```

---

# 6. CONFIG.PY

```python
# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration — shared by all environments."""

    SECRET_KEY           = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_SECRET_KEY       = os.getenv('JWT_SECRET_KEY', 'jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False          # Set True to log SQL queries

    # MySQL connection string
    DB_HOST     = os.getenv('DB_HOST', 'localhost')
    DB_PORT     = os.getenv('DB_PORT', '3306')
    DB_NAME     = os.getenv('DB_NAME', 'fitness_db')
    DB_USER     = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )

    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    FRONTEND_ORIGIN   = os.getenv('FRONTEND_ORIGIN', 'http://localhost:3000')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)


# Map string name to class (used in app.py)
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig
}
```

---

# 7. APP.PY — APP FACTORY

```python
# app.py
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
    app.config.from_object(config_map[env])

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

    # Global error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"status": "error", "message": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    # Health check route
    @app.route('/health')
    def health():
        return jsonify({"status": "ok", "version": "1.0.0"})

    # Start background scheduler
    if not scheduler.running:
        scheduler.start()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

# 8. MODELS (SQLAlchemy)

## models/user.py
```python
from extensions import db
from datetime import datetime

class User(db.Model):
    """Represents an authenticated user account."""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.Enum('user', 'admin'), default='user')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile         = db.relationship('HealthProfile',   backref='user', uselist=False, cascade='all, delete')
    activity_logs   = db.relationship('ActivityLog',     backref='user', cascade='all, delete')
    recommendations = db.relationship('Recommendation',  backref='user', cascade='all, delete')
    workout_plans   = db.relationship('WorkoutPlan',     backref='user', cascade='all, delete')
    reminders       = db.relationship('Reminder',        backref='user', cascade='all, delete')

    def to_dict(self):
        return {
            'id':         self.id,
            'full_name':  self.full_name,
            'email':      self.email,
            'role':       self.role,
            'created_at': self.created_at.isoformat()
        }
```

## models/health_profile.py
```python
from extensions import db
from datetime import datetime

class HealthProfile(db.Model):
    """Stores health metrics and fitness goals for a user."""
    __tablename__ = 'health_profiles'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    age            = db.Column(db.Integer, nullable=False)
    gender         = db.Column(db.Enum('male', 'female', 'other'), nullable=False)
    height_cm      = db.Column(db.Numeric(5, 2), nullable=False)
    weight_kg      = db.Column(db.Numeric(5, 2), nullable=False)
    activity_level = db.Column(db.Enum('sedentary', 'light', 'moderate', 'active'), nullable=False)
    sleep_hours    = db.Column(db.Numeric(4, 2), default=7.0)
    food_habits    = db.Column(db.Enum('veg', 'non-veg', 'vegan', 'keto', 'paleo'), default='non-veg')
    fitness_goal   = db.Column(db.Enum('weight_loss', 'muscle_gain', 'maintenance'), nullable=False)
    bmi            = db.Column(db.Numeric(5, 2))
    bmr            = db.Column(db.Numeric(8, 2))
    daily_calories = db.Column(db.Integer)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id':             self.id,
            'user_id':        self.user_id,
            'age':            self.age,
            'gender':         self.gender,
            'height_cm':      float(self.height_cm),
            'weight_kg':      float(self.weight_kg),
            'activity_level': self.activity_level,
            'sleep_hours':    float(self.sleep_hours) if self.sleep_hours else 7.0,
            'food_habits':    self.food_habits,
            'fitness_goal':   self.fitness_goal,
            'bmi':            float(self.bmi) if self.bmi else None,
            'bmr':            float(self.bmr) if self.bmr else None,
            'daily_calories': self.daily_calories
        }
```

## models/activity_log.py
```python
from extensions import db
from datetime import datetime, date

class ActivityLog(db.Model):
    """One log entry: meal, workout, water, or sleep."""
    __tablename__ = 'activity_logs'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    log_date     = db.Column(db.Date, nullable=False, default=date.today, index=True)
    log_type     = db.Column(db.Enum('meal', 'workout', 'water', 'sleep'), nullable=False)
    description  = db.Column(db.String(255))
    calories_in  = db.Column(db.Integer, default=0)
    calories_out = db.Column(db.Integer, default=0)
    water_ml     = db.Column(db.Integer, default=0)
    sleep_hours  = db.Column(db.Numeric(4, 2), default=0)
    duration_min = db.Column(db.Integer, default=0)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':           self.id,
            'log_type':     self.log_type,
            'description':  self.description,
            'calories_in':  self.calories_in,
            'calories_out': self.calories_out,
            'water_ml':     self.water_ml,
            'sleep_hours':  float(self.sleep_hours),
            'duration_min': self.duration_min,
            'log_date':     str(self.log_date),
            'created_at':   self.created_at.isoformat()
        }
```

## models/recommendation.py
```python
from extensions import db
from datetime import datetime

class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    diet_plan      = db.Column(db.JSON)
    workout_plan   = db.Column(db.JSON)
    daily_calories = db.Column(db.Integer)
    weekly_tips    = db.Column(db.JSON)
    bmi_category   = db.Column(db.String(50))
    generated_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'bmi_category':   self.bmi_category,
            'daily_calories': self.daily_calories,
            'diet_plan':      self.diet_plan,
            'workout_plan':   self.workout_plan,
            'weekly_tips':    self.weekly_tips,
            'generated_at':   self.generated_at.isoformat()
        }
```

---

# 9. SCHEMAS (Marshmallow Validation)

## schemas/auth_schema.py
```python
from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class RegisterSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email     = fields.Email(required=True)
    password  = fields.Str(required=True, validate=validate.Length(min=6, max=128))

    @validates('password')
    def validate_password_strength(self, value):
        # At least one letter and one number
        if not re.search(r'[A-Za-z]', value) or not re.search(r'[0-9]', value):
            raise ValidationError('Password must contain at least one letter and one number')


class LoginSchema(Schema):
    email    = fields.Email(required=True)
    password = fields.Str(required=True)
```

## schemas/profile_schema.py
```python
from marshmallow import Schema, fields, validate

class HealthProfileSchema(Schema):
    age            = fields.Int(required=True, validate=validate.Range(min=10, max=120))
    gender         = fields.Str(required=True, validate=validate.OneOf(['male', 'female', 'other']))
    height_cm      = fields.Float(required=True, validate=validate.Range(min=50, max=280))
    weight_kg      = fields.Float(required=True, validate=validate.Range(min=10, max=500))
    activity_level = fields.Str(required=True, validate=validate.OneOf(['sedentary','light','moderate','active']))
    sleep_hours    = fields.Float(missing=7.0, validate=validate.Range(min=0, max=24))
    food_habits    = fields.Str(missing='non-veg', validate=validate.OneOf(['veg','non-veg','vegan','keto','paleo']))
    fitness_goal   = fields.Str(required=True, validate=validate.OneOf(['weight_loss','muscle_gain','maintenance']))
```

## schemas/activity_schema.py
```python
from marshmallow import Schema, fields, validate

class ActivityLogSchema(Schema):
    log_type     = fields.Str(required=True, validate=validate.OneOf(['meal','workout','water','sleep']))
    description  = fields.Str(missing=None)
    calories_in  = fields.Int(missing=0, validate=validate.Range(min=0))
    calories_out = fields.Int(missing=0, validate=validate.Range(min=0))
    water_ml     = fields.Int(missing=0, validate=validate.Range(min=0))
    sleep_hours  = fields.Float(missing=0.0)
    duration_min = fields.Int(missing=0)
    log_date     = fields.Date(missing=None)   # defaults to today if omitted
```

---

# 10. MIDDLEWARE

## middleware/auth_middleware.py
```python
# middleware/auth_middleware.py
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User

def jwt_required_custom(f):
    """
    Custom JWT middleware decorator.
    Verifies token, loads user from DB, passes user_id to controller.
    Usage: @jwt_required_custom
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user    = User.query.get(user_id)
            if not user:
                return jsonify({"status": "error", "message": "User not found"}), 401
        except Exception as e:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401
        return f(*args, current_user=user, **kwargs)
    return decorated
```

## middleware/validation_middleware.py
```python
# middleware/validation_middleware.py
from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError

def validate_body(schema_class):
    """
    Decorator: validates request JSON body against a Marshmallow schema.
    Injects validated data as `validated_data` keyword argument.
    Usage: @validate_body(RegisterSchema)
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            schema = schema_class()
            json_data = request.get_json(silent=True)
            if json_data is None:
                return jsonify({"status": "error", "message": "Request body must be JSON"}), 400
            try:
                validated = schema.load(json_data)
            except ValidationError as err:
                return jsonify({
                    "status": "error",
                    "message": "Validation failed",
                    "errors": err.messages
                }), 400
            return f(*args, validated_data=validated, **kwargs)
        return decorated
    return decorator
```

---

# 11. UTILS

## utils/bmi_calculator.py
```python
# utils/bmi_calculator.py

ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light':     1.375,
    'moderate':  1.55,
    'active':    1.725
}

GOAL_CALORIE_ADJUSTMENTS = {
    'weight_loss':  -500,   # calorie deficit
    'muscle_gain':  +300,   # calorie surplus
    'maintenance':     0    # no adjustment
}

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """BMI = weight(kg) / height(m)^2"""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)

def get_bmi_category(bmi: float) -> str:
    """Returns human-readable BMI category."""
    if bmi < 18.5:  return 'Underweight'
    if bmi < 25.0:  return 'Normal'
    if bmi < 30.0:  return 'Overweight'
    return 'Obese'

def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor Equation.
    Most accurate for most people.
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender == 'male':
        return round(base + 5, 2)
    else:
        return round(base - 161, 2)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Total Daily Energy Expenditure = BMR × activity multiplier."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier, 2)

def calculate_daily_calories(tdee: float, goal: str) -> int:
    """Adjust TDEE based on fitness goal."""
    adjustment = GOAL_CALORIE_ADJUSTMENTS.get(goal, 0)
    return max(1200, int(tdee + adjustment))   # never below 1200 kcal
```

## utils/recommendation_engine.py
```python
# utils/recommendation_engine.py
from utils.bmi_calculator import get_bmi_category
from utils.diet_templates import DIET_TEMPLATES
from utils.workout_templates import WORKOUT_TEMPLATES

WEEKLY_TIPS = {
    'weight_loss': [
        "Drink 3L water daily — it boosts metabolism.",
        "Walk 10,000 steps per day as a baseline.",
        "Avoid processed sugars and trans fats.",
        "Track every meal — awareness reduces overeating.",
        "Sleep 7-8 hours — poor sleep increases hunger hormones."
    ],
    'muscle_gain': [
        "Eat 1.6-2.2g protein per kg of body weight.",
        "Progressive overload: increase weight each week.",
        "Rest muscles 48 hours between same-group sessions.",
        "Creatine monohydrate is the most evidence-backed supplement.",
        "Prioritize compound lifts: squat, deadlift, bench press."
    ],
    'maintenance': [
        "Consistency beats perfection — stick to your routine.",
        "Maintain your calorie balance — log weekly, not daily.",
        "Mix cardio and strength to preserve both fitness types.",
        "Stay hydrated — 2.5-3L daily.",
        "Schedule one active recovery day per week."
    ]
}

def generate_recommendation(profile) -> dict:
    """
    Rule-based engine.
    Takes a HealthProfile object, returns recommendation dict.
    """
    bmi          = float(profile.bmi)
    goal         = profile.fitness_goal
    food_pref    = profile.food_habits
    daily_cal    = profile.daily_calories

    bmi_cat = get_bmi_category(bmi)

    # Select diet template
    if goal == 'muscle_gain' or bmi < 18.5:
        diet_key    = 'high_protein'
        workout_key = 'strength'
    elif goal == 'weight_loss' or bmi >= 25:
        diet_key    = 'low_cal'
        workout_key = 'cardio'
    else:
        diet_key    = 'balanced'
        workout_key = 'mixed'

    # Food preference: vegan/veg/keto use different templates
    food_key = food_pref if food_pref in DIET_TEMPLATES[diet_key] else 'non-veg'

    diet_plan    = DIET_TEMPLATES[diet_key][food_key]
    workout_plan = WORKOUT_TEMPLATES[workout_key]
    tips         = WEEKLY_TIPS.get(goal, WEEKLY_TIPS['maintenance'])

    return {
        'bmi_category':   bmi_cat,
        'daily_calories': daily_cal,
        'diet_plan':      diet_plan,
        'workout_plan':   workout_plan,
        'weekly_tips':    tips
    }
```

## utils/diet_templates.py
```python
# utils/diet_templates.py
# Pre-defined meal templates per goal and food preference.
# Expand with more variety for production.

DIET_TEMPLATES = {
    'low_cal': {
        'non-veg': {
            'breakfast': {'meal': 'Oats with banana + green tea', 'kcal': 380},
            'lunch':     {'meal': 'Grilled chicken salad + whole wheat roti', 'kcal': 550},
            'snack':     {'meal': 'Mixed nuts + apple', 'kcal': 180},
            'dinner':    {'meal': 'Steamed fish + stir-fried vegetables', 'kcal': 450}
        },
        'veg': {
            'breakfast': {'meal': 'Upma + green tea', 'kcal': 320},
            'lunch':     {'meal': 'Dal + brown rice + salad', 'kcal': 500},
            'snack':     {'meal': 'Sprout chaat', 'kcal': 160},
            'dinner':    {'meal': 'Vegetable soup + whole wheat bread', 'kcal': 380}
        },
        'vegan': {
            'breakfast': {'meal': 'Smoothie bowl (oat milk + berries)', 'kcal': 340},
            'lunch':     {'meal': 'Quinoa salad + chickpeas', 'kcal': 480},
            'snack':     {'meal': 'Apple + almond butter', 'kcal': 190},
            'dinner':    {'meal': 'Lentil soup + rye bread', 'kcal': 400}
        }
    },
    'high_protein': {
        'non-veg': {
            'breakfast': {'meal': 'Egg white omelette + whole wheat toast', 'kcal': 420},
            'lunch':     {'meal': 'Chicken breast + sweet potato + broccoli', 'kcal': 650},
            'snack':     {'meal': 'Protein shake + banana', 'kcal': 300},
            'dinner':    {'meal': 'Salmon + brown rice + asparagus', 'kcal': 680}
        },
        'veg': {
            'breakfast': {'meal': 'Paneer scramble + multigrain toast', 'kcal': 440},
            'lunch':     {'meal': 'Rajma + brown rice + curd', 'kcal': 620},
            'snack':     {'meal': 'Roasted chana + nuts', 'kcal': 280},
            'dinner':    {'meal': 'Tofu stir-fry + quinoa', 'kcal': 580}
        }
    },
    'balanced': {
        'non-veg': {
            'breakfast': {'meal': 'Poha + boiled egg + tea', 'kcal': 400},
            'lunch':     {'meal': 'Chicken curry + rice + salad', 'kcal': 600},
            'snack':     {'meal': 'Fruit bowl + yogurt', 'kcal': 200},
            'dinner':    {'meal': 'Dal + roti + sautéed veggies', 'kcal': 550}
        },
        'veg': {
            'breakfast': {'meal': 'Idli + sambar + coconut chutney', 'kcal': 350},
            'lunch':     {'meal': 'Mixed dal + rice + papad + salad', 'kcal': 560},
            'snack':     {'meal': 'Makhana + green tea', 'kcal': 150},
            'dinner':    {'meal': 'Paneer curry + roti', 'kcal': 520}
        }
    }
}
```

## utils/workout_templates.py
```python
# utils/workout_templates.py

WORKOUT_TEMPLATES = {
    'cardio': {
        'Mon': [
            {'name': 'Brisk Walk / Jog', 'duration_min': 30, 'sets': 0, 'reps': 0},
            {'name': 'Core Crunches',    'duration_min': 0,  'sets': 3, 'reps': 20}
        ],
        'Tue': [
            {'name': 'Cycling / Stationary Bike', 'duration_min': 30, 'sets': 0, 'reps': 0}
        ],
        'Wed': [
            {'name': 'Rest / Light Yoga',  'duration_min': 20, 'sets': 0, 'reps': 0}
        ],
        'Thu': [
            {'name': 'HIIT Circuit',        'duration_min': 25, 'sets': 0, 'reps': 0},
            {'name': 'Jumping Jacks',       'duration_min': 0,  'sets': 3, 'reps': 30}
        ],
        'Fri': [
            {'name': 'Swimming / Skipping', 'duration_min': 30, 'sets': 0, 'reps': 0}
        ],
        'Sat': [
            {'name': 'Long Walk / Hike',    'duration_min': 45, 'sets': 0, 'reps': 0}
        ],
        'Sun': [
            {'name': 'Rest & Recovery',     'duration_min': 0,  'sets': 0, 'reps': 0}
        ]
    },
    'strength': {
        'Mon': [
            {'name': 'Bench Press',   'duration_min': 0, 'sets': 4, 'reps': 10},
            {'name': 'Dumbbell Curl', 'duration_min': 0, 'sets': 3, 'reps': 12},
            {'name': 'Push-ups',      'duration_min': 0, 'sets': 3, 'reps': 15}
        ],
        'Tue': [
            {'name': 'Squats',        'duration_min': 0, 'sets': 4, 'reps': 12},
            {'name': 'Lunges',        'duration_min': 0, 'sets': 3, 'reps': 10},
            {'name': 'Leg Press',     'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Wed': [
            {'name': 'Rest / Stretching', 'duration_min': 20, 'sets': 0, 'reps': 0}
        ],
        'Thu': [
            {'name': 'Deadlifts',     'duration_min': 0, 'sets': 4, 'reps': 8},
            {'name': 'Pull-ups',      'duration_min': 0, 'sets': 3, 'reps': 8},
            {'name': 'Rows',          'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Fri': [
            {'name': 'Shoulder Press', 'duration_min': 0, 'sets': 4, 'reps': 10},
            {'name': 'Lateral Raise',  'duration_min': 0, 'sets': 3, 'reps': 15},
            {'name': 'Tricep Dips',    'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Sat': [
            {'name': 'Full Body Circuit', 'duration_min': 30, 'sets': 0, 'reps': 0}
        ],
        'Sun': [
            {'name': 'Rest & Recovery',   'duration_min': 0,  'sets': 0, 'reps': 0}
        ]
    },
    'mixed': {
        'Mon': [{'name': '30min Cardio + Core', 'duration_min': 40, 'sets': 0, 'reps': 0}],
        'Tue': [{'name': 'Upper Body Strength', 'duration_min': 0,  'sets': 3, 'reps': 12}],
        'Wed': [{'name': 'Rest or Yoga',        'duration_min': 20, 'sets': 0, 'reps': 0}],
        'Thu': [{'name': 'HIIT 25min',          'duration_min': 25, 'sets': 0, 'reps': 0}],
        'Fri': [{'name': 'Lower Body Strength', 'duration_min': 0,  'sets': 3, 'reps': 12}],
        'Sat': [{'name': '45min Steady Cardio', 'duration_min': 45, 'sets': 0, 'reps': 0}],
        'Sun': [{'name': 'Rest',                'duration_min': 0,  'sets': 0, 'reps': 0}]
    }
}
```

---

# 12. CONTROLLERS

## controllers/auth_controller.py
```python
from flask import jsonify
from extensions import db, bcrypt
from flask_jwt_extended import create_access_token
from models.user import User


def register_user(data: dict):
    """Create a new user account."""
    if User.query.filter_by(email=data['email'].lower()).first():
        return jsonify({"status": "error", "message": "Email already registered"}), 400

    hashed = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        full_name     = data['full_name'].strip(),
        email         = data['email'].lower(),
        password_hash = hashed
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"status": "success", "message": "User registered", "user_id": user.id}), 201


def login_user(data: dict):
    """Authenticate user and return JWT."""
    user = User.query.filter_by(email=data['email'].lower()).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, data['password']):
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({
        "status":       "success",
        "access_token": token,
        "user":         user.to_dict()
    }), 200
```

## controllers/profile_controller.py
```python
from flask import jsonify
from extensions import db
from models.health_profile import HealthProfile
from models.recommendation import Recommendation
from utils.bmi_calculator import calculate_bmi, calculate_bmr, calculate_tdee, calculate_daily_calories
from utils.recommendation_engine import generate_recommendation


def get_profile(user_id: int):
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"status": "error", "message": "Profile not found"}), 404
    return jsonify({"status": "success", "profile": profile.to_dict()}), 200


def save_profile(user_id: int, data: dict):
    """Create or update health profile. Auto-calculates BMI, BMR, TDEE."""

    # Calculate metrics
    bmi  = calculate_bmi(data['weight_kg'], data['height_cm'])
    bmr  = calculate_bmr(data['weight_kg'], data['height_cm'], data['age'], data['gender'])
    tdee = calculate_tdee(bmr, data['activity_level'])
    cal  = calculate_daily_calories(tdee, data['fitness_goal'])

    profile = HealthProfile.query.filter_by(user_id=user_id).first()

    if profile:
        # Update existing profile
        for key, val in data.items():
            setattr(profile, key, val)
        profile.bmi            = bmi
        profile.bmr            = bmr
        profile.daily_calories = cal
    else:
        # Create new profile
        profile = HealthProfile(
            user_id        = user_id,
            bmi            = bmi,
            bmr            = bmr,
            daily_calories = cal,
            **data
        )
        db.session.add(profile)

    db.session.commit()

    # Auto-regenerate recommendations after profile update
    _refresh_recommendations(user_id, profile)

    return jsonify({
        "status":         "success",
        "message":        "Profile saved",
        "bmi":            bmi,
        "bmr":            bmr,
        "daily_calories": cal
    }), 200


def _refresh_recommendations(user_id: int, profile):
    """Internal: regenerates and saves recommendation after profile change."""
    rec_data = generate_recommendation(profile)
    rec = Recommendation.query.filter_by(user_id=user_id).first()
    if rec:
        for k, v in rec_data.items():
            setattr(rec, k, v)
    else:
        rec = Recommendation(user_id=user_id, **rec_data)
        db.session.add(rec)
    db.session.commit()
```

## controllers/dashboard_controller.py
```python
from flask import jsonify
from models.activity_log import ActivityLog
from models.health_profile import HealthProfile
from models.recommendation import Recommendation
from utils.quote_generator import get_daily_quote
from datetime import date, timedelta
from sqlalchemy import func


def get_dashboard(user_id: int):
    profile = HealthProfile.query.filter_by(user_id=user_id).first()
    rec     = Recommendation.query.filter_by(user_id=user_id).first()
    today   = date.today()

    # Today's totals
    today_logs = ActivityLog.query.filter_by(user_id=user_id, log_date=today).all()
    cal_in  = sum(l.calories_in  for l in today_logs)
    cal_out = sum(l.calories_out for l in today_logs)
    water   = sum(l.water_ml     for l in today_logs)

    # Weekly chart data
    week_labels, week_in, week_out = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_logs = ActivityLog.query.filter_by(user_id=user_id, log_date=d).all()
        week_labels.append(d.strftime('%a'))
        week_in.append(sum(l.calories_in  for l in day_logs))
        week_out.append(sum(l.calories_out for l in day_logs))

    # Workout streak
    streak = _calculate_streak(user_id, today)

    daily_goal = profile.daily_calories if profile else 2000
    pct        = min(int((cal_in / daily_goal) * 100), 100) if daily_goal else 0

    return jsonify({
        "status": "success",
        "dashboard": {
            "bmi":                  float(profile.bmi) if profile else None,
            "bmi_category":         rec.bmi_category if rec else "—",
            "today_calories_in":    cal_in,
            "today_calories_out":   cal_out,
            "daily_calorie_goal":   daily_goal,
            "goal_progress_pct":    pct,
            "workout_streak":       streak,
            "water_today_ml":       water,
            "water_goal_ml":        3000,
            "weekly_chart": {
                "labels":      week_labels,
                "calories_in": week_in,
                "calories_out":week_out
            },
            "motivational_quote":   get_daily_quote(),
            "this_week_tip":        (rec.weekly_tips[0] if rec and rec.weekly_tips else "Stay consistent!")
        }
    }), 200


def _calculate_streak(user_id: int, today: date) -> int:
    """Count consecutive days with at least one workout logged."""
    streak = 0
    d = today
    while True:
        workouts = ActivityLog.query.filter_by(
            user_id=user_id, log_date=d, log_type='workout'
        ).count()
        if workouts == 0:
            break
        streak += 1
        d -= timedelta(days=1)
    return streak
```

## controllers/ai_controller.py
```python
# controllers/ai_controller.py
import os
import anthropic
from flask import jsonify
from models.health_profile import HealthProfile


def diet_chat(user_id: int, message: str):
    """Send user message to Claude AI with their health context."""

    profile = HealthProfile.query.filter_by(user_id=user_id).first()

    # Build a personalized system prompt using the user's profile
    if profile:
        system_prompt = f"""You are a professional AI diet and fitness assistant.
The user you are helping has the following profile:
- Age: {profile.age}, Gender: {profile.gender}
- BMI: {profile.bmi} ({_bmi_cat(float(profile.bmi))})
- Fitness Goal: {profile.fitness_goal}
- Food Preference: {profile.food_habits}
- Daily Calorie Target: {profile.daily_calories} kcal

Provide short, practical, personalized advice.
Keep responses under 4 sentences unless detailed meal plans are requested.
Be friendly, encouraging, and evidence-based."""
    else:
        system_prompt = "You are a helpful AI diet and fitness assistant. Give friendly, practical advice."

    try:
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        response = client.messages.create(
            model      = "claude-sonnet-4-20250514",
            max_tokens = 512,
            system     = system_prompt,
            messages   = [{"role": "user", "content": message}]
        )

        reply = response.content[0].text

        return jsonify({
            "status": "success",
            "reply":  reply,
            "speak":  True      # Frontend will use TTS if voice mode is on
        }), 200

    except Exception as e:
        return jsonify({
            "status":  "error",
            "message": f"AI service error: {str(e)}"
        }), 500


def _bmi_cat(bmi: float) -> str:
    if bmi < 18.5: return 'Underweight'
    if bmi < 25:   return 'Normal'
    if bmi < 30:   return 'Overweight'
    return 'Obese'
```

---

# 13. ROUTES (BLUEPRINTS)

## routes/__init__.py
```python
# routes/__init__.py
def register_blueprints(app):
    """Register all route blueprints with the Flask app."""
    from routes.auth_routes           import auth_bp
    from routes.profile_routes        import profile_bp
    from routes.recommendation_routes import recommend_bp
    from routes.activity_routes       import activity_bp
    from routes.dashboard_routes      import dashboard_bp
    from routes.food_routes           import food_bp
    from routes.workout_routes        import workout_bp
    from routes.trainer_routes        import trainer_bp
    from routes.doctor_routes         import doctor_bp
    from routes.ai_routes             import ai_bp
    from routes.reminder_routes       import reminder_bp
    from routes.progress_routes       import progress_bp
    from routes.export_routes         import export_bp

    blueprints = [
        auth_bp, profile_bp, recommend_bp, activity_bp,
        dashboard_bp, food_bp, workout_bp, trainer_bp,
        doctor_bp, ai_bp, reminder_bp, progress_bp, export_bp
    ]
    for bp in blueprints:
        app.register_blueprint(bp)
```

## routes/auth_routes.py
```python
from flask import Blueprint
from extensions import limiter
from middleware.validation_middleware import validate_body
from schemas.auth_schema import RegisterSchema, LoginSchema
from controllers.auth_controller import register_user, login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("10 per hour")       # prevent spam registrations
@validate_body(RegisterSchema)
def register(validated_data):
    return register_user(validated_data)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("20 per hour")       # brute-force protection
@validate_body(LoginSchema)
def login(validated_data):
    return login_user(validated_data)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # JWT is stateless — client just deletes the token
    from flask import jsonify
    return jsonify({"status": "success", "message": "Logged out"}), 200
```

## routes/profile_routes.py
```python
from flask import Blueprint
from middleware.auth_middleware import jwt_required_custom
from middleware.validation_middleware import validate_body
from schemas.profile_schema import HealthProfileSchema
from controllers.profile_controller import get_profile, save_profile

profile_bp = Blueprint('profile', __name__, url_prefix='/api')

@profile_bp.route('/profile', methods=['GET'])
@jwt_required_custom
def profile_get(current_user):
    return get_profile(current_user.id)

@profile_bp.route('/profile', methods=['POST'])
@jwt_required_custom
@validate_body(HealthProfileSchema)
def profile_save(current_user, validated_data):
    return save_profile(current_user.id, validated_data)
```

## routes/ai_routes.py
```python
from flask import Blueprint, request, jsonify
from middleware.auth_middleware import jwt_required_custom
from controllers.ai_controller import diet_chat

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/diet-chat', methods=['POST'])
@jwt_required_custom
def chat(current_user):
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({"status": "error", "message": "Message is required"}), 400
    return diet_chat(current_user.id, message)
```

*(All other route files follow the same pattern: Blueprint → middleware → controller call)*

---

# 14. API CONTRACT (BACKEND SIDE)

All routes, methods, auth requirements, and controllers mapped:

| Method | URL | Auth | Rate Limit | Controller Function | Schema |
|---|---|---|---|---|---|
| POST | /api/register | No | 10/hr | register_user | RegisterSchema |
| POST | /api/login | No | 20/hr | login_user | LoginSchema |
| POST | /api/logout | No | — | inline | — |
| GET | /api/profile | Yes | — | get_profile | — |
| POST | /api/profile | Yes | — | save_profile | HealthProfileSchema |
| GET | /api/dashboard | Yes | — | get_dashboard | — |
| GET | /api/recommendations | Yes | — | get_recommendation | — |
| POST | /api/activity | Yes | — | log_activity | ActivityLogSchema |
| GET | /api/activity | Yes | — | get_activity | — |
| GET | /api/food/search | Yes | — | search_food | — |
| POST | /api/food/scan | Yes | — | scan_barcode | — |
| GET | /api/workout/plan | Yes | — | get_plan | — |
| POST | /api/workout/plan | Yes | — | save_plan | WorkoutPlanSchema |
| POST | /api/workout/timer | Yes | — | log_timer | — |
| GET | /api/trainers | Yes | — | list_trainers | — |
| GET | /api/doctors | Yes | — | list_doctors | — |
| POST | /api/ai/diet-chat | Yes | 60/hr | diet_chat | — |
| GET | /api/reminders | Yes | — | list_reminders | — |
| POST | /api/reminders | Yes | — | add_reminder | ReminderSchema |
| DELETE | /api/reminders/<id> | Yes | — | delete_reminder | — |
| GET | /api/progress | Yes | — | get_progress | — |
| GET | /api/export/pdf | Yes | 5/hr | generate_pdf | — |

### Standard Response Envelope
```python
# Success
{"status": "success", "data_key": ...}

# Error
{"status": "error", "message": "Human readable message", "errors": {...}}
```

---

# 15. AI INTEGRATION (CLAUDE API)

- Uses `anthropic` Python SDK
- Model: `claude-sonnet-4-20250514`
- System prompt is personalized per user (injects BMI, goal, food pref, calorie target)
- Max tokens: 512 (keeps responses concise for voice output)
- Rate limited: 60 requests/hour per user

**Key file:** `controllers/ai_controller.py` (shown in Section 12)

---

# 16. PDF EXPORT

```python
# utils/pdf_generator.py
from weasyprint import HTML
from flask import current_app
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from datetime import date, timedelta


def generate_health_report(user) -> bytes:
    """Generate a PDF health report for the user. Returns PDF bytes."""

    profile = HealthProfile.query.filter_by(user_id=user.id).first()
    today = date.today()
    week_ago = today - timedelta(days=7)

    # Gather last 7 days of logs
    logs = ActivityLog.query.filter(
        ActivityLog.user_id == user.id,
        ActivityLog.log_date >= week_ago
    ).all()

    total_in  = sum(l.calories_in  for l in logs)
    total_out = sum(l.calories_out for l in logs)

    html_content = f"""
    <html>
    <head>
      <style>
        body {{ font-family: Arial, sans-serif; padding: 40px; color: #333; }}
        h1   {{ color: #00d4aa; }}
        .stat {{ display: inline-block; margin: 10px 20px 10px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f0f4f8; }}
      </style>
    </head>
    <body>
      <h1>Health Report — {user.full_name}</h1>
      <p>Generated: {today.strftime('%B %d, %Y')}</p>
      <hr>
      <h2>Body Metrics</h2>
      <div class="stat"><strong>BMI:</strong> {profile.bmi if profile else '—'}</div>
      <div class="stat"><strong>Weight:</strong> {profile.weight_kg if profile else '—'} kg</div>
      <div class="stat"><strong>Goal:</strong> {profile.fitness_goal if profile else '—'}</div>
      <div class="stat"><strong>Daily Target:</strong> {profile.daily_calories if profile else '—'} kcal</div>
      <h2>Last 7 Days Summary</h2>
      <div class="stat"><strong>Total Calories In:</strong> {total_in} kcal</div>
      <div class="stat"><strong>Total Calories Burned:</strong> {total_out} kcal</div>
    </body>
    </html>
    """

    return HTML(string=html_content).write_pdf()
```

```python
# controllers/export_controller.py
from flask import Response
from utils.pdf_generator import generate_health_report

def export_pdf(user):
    pdf_bytes = generate_health_report(user)
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=health-report.pdf'}
    )
```

---

# 17. SCHEDULER — DAILY REMINDERS

```python
# Called from app.py after scheduler.start()
# utils/reminder_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

def setup_reminder_job(scheduler, app):
    """Check every minute if any reminder is due."""

    @scheduler.scheduled_job('interval', minutes=1, id='reminder_check')
    def check_reminders():
        with app.app_context():
            from models.reminder import Reminder
            now_time = datetime.now().strftime('%H:%M')
            active = Reminder.query.filter_by(is_active=True).all()
            for r in active:
                if r.remind_at and r.remind_at.strftime('%H:%M') == now_time:
                    # In production: send push notification or email
                    # For MVP: log to console (frontend polls reminders)
                    print(f"[REMINDER] User {r.user_id}: {r.message}")
```

For real push notifications, integrate:
- **Web Push API** (via `pywebpush`) for browser notifications
- **Email** (via Flask-Mail or SendGrid) for email reminders

---

# 18. SECURITY CHECKLIST

| Item | Implementation |
|---|---|
| Password hashing | `bcrypt` with cost factor 12 |
| JWT auth | `Flask-JWT-Extended`, 24hr expiry |
| Protected routes | `@jwt_required_custom` on all private endpoints |
| Input validation | Marshmallow schema on every POST |
| SQL injection prevention | SQLAlchemy ORM (no raw SQL) |
| Rate limiting | Flask-Limiter on login, register, AI endpoints |
| CORS | Only allows configured `FRONTEND_ORIGIN` |
| Env secrets | `.env` file, never hardcoded |
| Error messages | Never expose stack traces in production |
| XSS prevention | Flask auto-escapes template output; API returns JSON only |

---

# 19. SETUP & RUN INSTRUCTIONS

```bash
# 1. Clone repo
git clone https://github.com/yourname/fitness-backend.git
cd fitness-backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env from template
cp .env.example .env
# Edit .env: add DB credentials, JWT secret, Anthropic API key

# 5. Create MySQL database
mysql -u root -p -e "CREATE DATABASE fitness_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 6. Run database migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 7. (Optional) Seed food items data
python seed_food_data.py

# 8. Start development server
python app.py
# OR: flask run --port=5000

# Server running at: http://localhost:5000
# Health check: http://localhost:5000/health
```

---

# 20. DEPLOYMENT NOTES

## Production Setup (Ubuntu VPS with Nginx)

```bash
# Gunicorn (production WSGI server)
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"

# Nginx config (reverse proxy)
# /etc/nginx/sites-available/fitness-api
server {
    listen 80;
    server_name api.yourapp.com;
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# SSL (HTTPS)
sudo certbot --nginx -d api.yourapp.com
```

## Environment Variables for Production
```
FLASK_ENV=production
SECRET_KEY=<strong-random-64-char-key>
JWT_SECRET_KEY=<strong-random-64-char-key>
DATABASE_URL=mysql+pymysql://user:pass@db-host/fitness_db
ANTHROPIC_API_KEY=sk-ant-...
FRONTEND_ORIGIN=https://yourapp.com
```

## Codex / Antigravity Deployment
- Set all environment variables in the platform's secrets dashboard
- Point `DATABASE_URL` to a managed MySQL instance (PlanetScale, AWS RDS, etc.)
- Set `FLASK_ENV=production`
- Use `gunicorn app:create_app()` as the start command

---

*Backend Plan v1.0 — fitness-backend repo*  
*Python 3.11 · Flask · MySQL · JWT · Claude AI · 22 API Endpoints · Production-Ready*
