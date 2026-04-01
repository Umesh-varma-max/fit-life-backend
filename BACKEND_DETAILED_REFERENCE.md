# FitLife Backend Detailed Reference

## Overview

FitLife backend is a Flask-based REST API for an AI-powered fitness and diet management platform. It handles:

- authentication with JWT
- health profile creation and updates
- dashboard summaries
- diet and workout recommendations
- food lookup and intake logging
- workout planning and workout session logging
- progress summaries
- trainer and doctor directory data
- reminders
- AI diet chat via Groq
- PDF export

The backend is structured using the Flask application factory pattern and is deployed on Render. It now supports Neon PostgreSQL in production through `DATABASE_URL`.

---

## Core Stack

- Python 3.10+
- Flask 3
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- Flask-JWT-Extended
- Flask-Bcrypt
- Flask-CORS
- Flask-Limiter
- APScheduler
- Marshmallow
- Groq SDK
- fpdf2
- PostgreSQL via `psycopg`

---

## Entry Point And App Bootstrap

### Main file

- [app.py](/C:/Users/rajus/fitlife/backend/app.py)

### What `create_app()` does

1. creates the Flask app
2. loads config using `FLASK_ENV`
3. initializes shared extensions
4. configures CORS for `/api/*`
5. registers all blueprints
6. imports models so migrations can discover metadata
7. registers global error handlers
8. exposes `/health`
9. starts the background scheduler if not already running

### Runtime behavior

- local run: `python app.py`
- production entrypoint: [wsgi.py](/C:/Users/rajus/fitlife/backend/wsgi.py)
- Render start command: `gunicorn wsgi:app`

---

## Configuration

### Config file

- [config.py](/C:/Users/rajus/fitlife/backend/config.py)

### Important config behavior

- `SECRET_KEY` and `JWT_SECRET_KEY` come from env vars
- JWT access tokens expire in 24 hours in development and 12 hours in production
- database connection prefers `DATABASE_URL`
- if `DATABASE_URL` is missing, it falls back to individual DB fields
- Neon/Postgres URLs are normalized to `postgresql+psycopg://...`
- `FRONTEND_ORIGIN` supports a single origin or a comma-separated list of origins

### Main env vars

- `FLASK_ENV`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `GROQ_API_KEY`
- `FRONTEND_ORIGIN`
- optional fallback DB vars:
  - `DB_DIALECT`
  - `DB_HOST`
  - `DB_PORT`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`

---

## Deployment

### Render config

- [render.yaml](/C:/Users/rajus/fitlife/backend/render.yaml)

### Render service settings

- type: `web`
- runtime: `python`
- build command: `pip install -r requirements.txt`
- start command: `gunicorn wsgi:app`
- health endpoint: `/health`

### Production database

- Neon PostgreSQL via `DATABASE_URL`

### CORS in production

`FRONTEND_ORIGIN` can now allow multiple frontends, for example:

```env
FRONTEND_ORIGIN=https://fitlife-frontend.onrender.com,https://fit-life-frontend.vercel.app
```

---

## Shared Extensions

### File

- [extensions.py](/C:/Users/rajus/fitlife/backend/extensions.py)

### Registered extensions

- `db`: SQLAlchemy ORM
- `jwt`: JWT token management
- `bcrypt`: password hashing
- `cors`: cross-origin access control
- `migrate`: Alembic migration integration
- `limiter`: request rate limiting
- `scheduler`: APScheduler background scheduler

### Default rate limits

- `200 per hour`
- `50 per minute`

---

## Project Structure

### Core files

- [app.py](/C:/Users/rajus/fitlife/backend/app.py): Flask factory and runtime entry
- [config.py](/C:/Users/rajus/fitlife/backend/config.py): environment-based configuration
- [extensions.py](/C:/Users/rajus/fitlife/backend/extensions.py): shared Flask extensions
- [requirements.txt](/C:/Users/rajus/fitlife/backend/requirements.txt): dependencies
- [wsgi.py](/C:/Users/rajus/fitlife/backend/wsgi.py): Gunicorn entrypoint
- [render.yaml](/C:/Users/rajus/fitlife/backend/render.yaml): Render deployment blueprint

### Major folders

- [controllers](/C:/Users/rajus/fitlife/backend/controllers): business logic
- [routes](/C:/Users/rajus/fitlife/backend/routes): blueprints and HTTP layer
- [models](/C:/Users/rajus/fitlife/backend/models): SQLAlchemy models
- [schemas](/C:/Users/rajus/fitlife/backend/schemas): Marshmallow validation
- [middleware](/C:/Users/rajus/fitlife/backend/middleware): JWT and body validation wrappers
- [utils](/C:/Users/rajus/fitlife/backend/utils): reusable domain helpers
- [migrations](/C:/Users/rajus/fitlife/backend/migrations): Alembic migration history

---

## Request Flow

Typical request flow:

1. request reaches a blueprint route in `routes/`
2. route applies middleware such as JWT validation or body validation
3. route calls a controller function
4. controller reads/writes models through SQLAlchemy
5. helpers from `utils/` are used for calculations, templates, or external AI calls
6. controller returns JSON response

For protected endpoints:

1. `verify_jwt_in_request()` validates the token
2. JWT identity is read as a string
3. middleware converts it back to `int`
4. current user is loaded from the database

---

## Middleware

### Files

- [auth_middleware.py](/C:/Users/rajus/fitlife/backend/middleware/auth_middleware.py)
- [validation_middleware.py](/C:/Users/rajus/fitlife/backend/middleware/validation_middleware.py)

### Responsibilities

#### Auth middleware

- verifies JWT presence and validity
- converts JWT identity back to integer user ID
- loads `current_user`
- rejects missing, invalid, expired, or orphaned tokens

#### Validation middleware

- reads JSON body
- validates against a Marshmallow schema
- injects `validated_data` into route handlers

---

## Models

### Model registry

- [models/__init__.py](/C:/Users/rajus/fitlife/backend/models/__init__.py)

### User-related models

#### [user.py](/C:/Users/rajus/fitlife/backend/models/user.py)

Stores account data:

- `id`
- `full_name`
- `email`
- `password_hash`
- `role`
- timestamps

#### [health_profile.py](/C:/Users/rajus/fitlife/backend/models/health_profile.py)

Stores user physical and goal data:

- age
- gender
- height
- weight
- activity level
- sleep hours
- food habits
- fitness goal
- BMI
- BMR
- daily calorie target

#### [activity_log.py](/C:/Users/rajus/fitlife/backend/models/activity_log.py)

Stores daily activity entries:

- meal
- workout
- water
- sleep

Includes:

- calories in
- calories out
- water ml
- sleep hours
- duration
- date

#### [recommendation.py](/C:/Users/rajus/fitlife/backend/models/recommendation.py)

Stores generated recommendation payloads:

- diet plan
- workout plan
- daily calories
- weekly tips
- BMI category

#### [reminder.py](/C:/Users/rajus/fitlife/backend/models/reminder.py)

Stores reminder records:

- reminder type
- message
- remind time
- repeat flag
- active flag

#### [workout_plan.py](/C:/Users/rajus/fitlife/backend/models/workout_plan.py)

Stores custom workout days:

- plan name
- day of week
- exercise JSON payload

### Lookup/reference models

#### [food_item.py](/C:/Users/rajus/fitlife/backend/models/food_item.py)

Stores searchable food catalog data:

- name
- calories per 100g
- macros
- barcode
- source

#### [trainer.py](/C:/Users/rajus/fitlife/backend/models/trainer.py)

Stores trainer listing data.

#### [doctor.py](/C:/Users/rajus/fitlife/backend/models/doctor.py)

Stores doctor listing data.

---

## Schemas

### Files

- [auth_schema.py](/C:/Users/rajus/fitlife/backend/schemas/auth_schema.py)
- [profile_schema.py](/C:/Users/rajus/fitlife/backend/schemas/profile_schema.py)
- [activity_schema.py](/C:/Users/rajus/fitlife/backend/schemas/activity_schema.py)
- [reminder_schema.py](/C:/Users/rajus/fitlife/backend/schemas/reminder_schema.py)
- [workout_schema.py](/C:/Users/rajus/fitlife/backend/schemas/workout_schema.py)

### Purpose

These schemas validate incoming request payloads before controller logic runs.

Examples:

- auth: register and login payloads
- profile: health profile fields and enums
- activity: activity logging payloads
- reminder: reminder creation payloads
- workout: workout plan day and exercise structure

---

## Controllers

### Auth

- [auth_controller.py](/C:/Users/rajus/fitlife/backend/controllers/auth_controller.py)

Handles:

- register user
- login user
- password hash verification
- JWT generation

Important detail:

- JWT identity is stored as `str(user.id)` to keep auth stable with newer JWT handling

### Profile

- [profile_controller.py](/C:/Users/rajus/fitlife/backend/controllers/profile_controller.py)

Handles:

- create or update profile
- BMI/BMR/TDEE calculation
- calorie target generation
- return current profile data

### Dashboard

- [dashboard_controller.py](/C:/Users/rajus/fitlife/backend/controllers/dashboard_controller.py)

Builds summary cards and dashboard metrics from profile, activities, and recommendations.

### Recommendation

- [recommendation_controller.py](/C:/Users/rajus/fitlife/backend/controllers/recommendation_controller.py)

Handles:

- reading cached recommendation
- generating recommendation when missing
- injecting enriched goal-based workout plans

### Activity

- [activity_controller.py](/C:/Users/rajus/fitlife/backend/controllers/activity_controller.py)

Handles:

- logging daily activity
- reading activity by date
- summary totals for calories, water, and sleep

### Food

- [food_controller.py](/C:/Users/rajus/fitlife/backend/controllers/food_controller.py)

Handles:

- food search
- food scan by barcode or name
- quantity-aware calorie and macro calculation
- meal feedback generation
- optional auto-log into activity history

### Workout

- [workout_controller.py](/C:/Users/rajus/fitlife/backend/controllers/workout_controller.py)

Handles:

- returning custom saved plans
- fallback goal-based weekly plans
- per-day duration totals
- estimated calorie burn
- exercise posture details
- timer workout logging

### Reminder

- [reminder_controller.py](/C:/Users/rajus/fitlife/backend/controllers/reminder_controller.py)

Handles create, list, and delete reminder flows.

### AI

- [ai_controller.py](/C:/Users/rajus/fitlife/backend/controllers/ai_controller.py)

Handles AI diet chat using Groq and fallback behavior when API results are unavailable.

### Progress

- [progress_controller.py](/C:/Users/rajus/fitlife/backend/controllers/progress_controller.py)

Builds weekly or monthly progress summaries from activity and profile data.

### Export

- [export_controller.py](/C:/Users/rajus/fitlife/backend/controllers/export_controller.py)

Generates PDF health reports.

### Directory controllers

- [trainer_controller.py](/C:/Users/rajus/fitlife/backend/controllers/trainer_controller.py)
- [doctor_controller.py](/C:/Users/rajus/fitlife/backend/controllers/doctor_controller.py)

These return filtered directory listings.

---

## Routes And API Surface

### Blueprint registration

- [routes/__init__.py](/C:/Users/rajus/fitlife/backend/routes/__init__.py)

### Route files

- [auth_routes.py](/C:/Users/rajus/fitlife/backend/routes/auth_routes.py)
- [profile_routes.py](/C:/Users/rajus/fitlife/backend/routes/profile_routes.py)
- [dashboard_routes.py](/C:/Users/rajus/fitlife/backend/routes/dashboard_routes.py)
- [recommendation_routes.py](/C:/Users/rajus/fitlife/backend/routes/recommendation_routes.py)
- [activity_routes.py](/C:/Users/rajus/fitlife/backend/routes/activity_routes.py)
- [food_routes.py](/C:/Users/rajus/fitlife/backend/routes/food_routes.py)
- [workout_routes.py](/C:/Users/rajus/fitlife/backend/routes/workout_routes.py)
- [trainer_routes.py](/C:/Users/rajus/fitlife/backend/routes/trainer_routes.py)
- [doctor_routes.py](/C:/Users/rajus/fitlife/backend/routes/doctor_routes.py)
- [ai_routes.py](/C:/Users/rajus/fitlife/backend/routes/ai_routes.py)
- [reminder_routes.py](/C:/Users/rajus/fitlife/backend/routes/reminder_routes.py)
- [progress_routes.py](/C:/Users/rajus/fitlife/backend/routes/progress_routes.py)
- [export_routes.py](/C:/Users/rajus/fitlife/backend/routes/export_routes.py)

### Main endpoints

#### Auth

- `POST /api/register`
- `POST /api/login`
- `POST /api/logout`

#### Profile

- `GET /api/profile`
- `POST /api/profile`

#### Dashboard and recommendations

- `GET /api/dashboard`
- `GET /api/recommendations`

#### Activity

- `POST /api/activity`
- `GET /api/activity`

#### Food

- `GET /api/food/search`
- `POST /api/food/scan`

#### Workout

- `GET /api/workout/plan`
- `POST /api/workout/plan`
- `POST /api/workout/timer`

#### Directories

- `GET /api/trainers`
- `GET /api/doctors`

#### AI and reminders

- `POST /api/ai/diet-chat`
- `GET /api/reminders`
- `POST /api/reminders`
- `DELETE /api/reminders/<id>`

#### Progress and export

- `GET /api/progress`
- `GET /api/export/pdf`

#### Health

- `GET /health`

---

## Utility Layer

### Files

- [bmi_calculator.py](/C:/Users/rajus/fitlife/backend/utils/bmi_calculator.py)
- [diet_templates.py](/C:/Users/rajus/fitlife/backend/utils/diet_templates.py)
- [recommendation_engine.py](/C:/Users/rajus/fitlife/backend/utils/recommendation_engine.py)
- [workout_templates.py](/C:/Users/rajus/fitlife/backend/utils/workout_templates.py)
- [pdf_generator.py](/C:/Users/rajus/fitlife/backend/utils/pdf_generator.py)
- [quote_generator.py](/C:/Users/rajus/fitlife/backend/utils/quote_generator.py)
- [validators.py](/C:/Users/rajus/fitlife/backend/utils/validators.py)

### Key utility responsibilities

#### BMI calculator

- BMI calculation
- BMI category
- BMR/TDEE support
- calorie target logic

#### Recommendation engine

- chooses diet template based on goal and food preference
- chooses workout template based on goal/BMI
- returns weekly tips

#### Workout templates

- contains goal-based workout template data
- enriches exercises with posture guidance
- estimates calorie burn and duration
- builds weekly workout plans

#### PDF generator

- creates downloadable health report PDFs

#### Validators

- normalization helpers such as email normalization

---

## Database And Migrations

### Migration folder

- [migrations](/C:/Users/rajus/fitlife/backend/migrations)

### Current migration state

- initial migration present in [f5b58c0adf38_initial_migration.py](/C:/Users/rajus/fitlife/backend/migrations/versions/f5b58c0adf38_initial_migration.py)

### Migration workflow

Typical commands:

```powershell
venv\Scripts\flask.exe --app app:create_app db upgrade
```

### Current hosted database path

- production database migrated from local MySQL into Neon PostgreSQL
- app now uses Neon through `DATABASE_URL`

---

## Seed Scripts

### Files

- [seed_food_data.py](/C:/Users/rajus/fitlife/backend/seed_food_data.py)
- [seed_trainers_doctors.py](/C:/Users/rajus/fitlife/backend/seed_trainers_doctors.py)

### Purpose

- seed food catalog
- seed trainer directory
- seed doctor directory

These are useful for fresh environments where data needs to exist before the UI is useful.

---

## Security And Auth Notes

### Strengths

- passwords are hashed with bcrypt
- protected endpoints use JWT
- request body validation is centralized
- rate limiting exists

### Important current behavior

- JWT identity is serialized as string and converted back to integer in middleware
- this prevents protected requests from failing after login

### Remaining production hardening ideas

- stricter secret management
- password reset flow
- email verification
- persistent limiter storage
- stronger scheduler job management

---

## Current Production Notes

### Live backend

- `https://fitlife-backend-rrd9.onrender.com`

### Health endpoint

- `https://fitlife-backend-rrd9.onrender.com/health`

### Allowed frontends

Configured through `FRONTEND_ORIGIN`, now supporting multiple origins.

Example:

```env
FRONTEND_ORIGIN=https://fitlife-frontend.onrender.com,https://fit-life-frontend.vercel.app
```

### Frontend integration requirement

The frontend must call the deployed backend URL, not `localhost`.

Expected API base URL:

```text
https://fitlife-backend-rrd9.onrender.com
```

---

## Backend Strength Summary

This backend is already a fairly complete product backend, not just a starter API. It has:

- full authentication flow
- user profile and health calculations
- rich dashboard and progress logic
- food intake analysis
- goal-based workout generation
- recommendation storage and retrieval
- AI chat integration
- reminder and export support
- deployed production runtime with Render + Neon

---

## Suggested Next Improvements

- add automated tests for auth, profile, food scan, and workout plan flows
- store rate limits in Redis or another shared backend for production
- add a root `/` route for a cleaner homepage response
- create a dedicated API base URL config file for the frontend
- add CI checks for migrations and basic endpoint health
- add admin or internal maintenance scripts for database and seeds

---

## Related Files

- [README.md](/C:/Users/rajus/fitlife/backend/README.md)
- [AGENT.md](/C:/Users/rajus/fitlife/backend/AGENT.md)
- [FitLife_Project_Status.md](/C:/Users/rajus/fitlife/backend/FitLife_Project_Status.md)
- [BACKEND_PLAN.md](/C:/Users/rajus/fitlife/backend/BACKEND_PLAN.md)
- [AI_FitnessApp_Blueprint.md](/C:/Users/rajus/fitlife/backend/AI_FitnessApp_Blueprint.md)

