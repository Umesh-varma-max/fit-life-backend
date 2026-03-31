# FitLife — AI Fitness Management System

## Project Context

This is a **full-stack AI-powered Fitness & Diet Management System** with:

- **Backend:** Flask 3.0 (Python) REST API with 22 endpoints, MySQL 8.0 via SQLAlchemy, JWT auth, Groq AI (Llama 3 70B)
- **Frontend:** Vanilla HTML/CSS/JavaScript with 12 pages, 19 JS modules, 8 CSS files — no frameworks

## Project Structure

```
fitlife/
├── backend/                    # Flask REST API (this repo)
│   ├── app.py                  # App factory entry point
│   ├── config.py               # Dev/Prod config (MySQL, JWT, CORS, Groq)
│   ├── extensions.py           # SQLAlchemy, JWT, Bcrypt, CORS, Migrate, Limiter, APScheduler
│   ├── requirements.txt        # 15 Python dependencies
│   ├── .env / .env.example     # Environment variables
│   ├── models/          (9)    # User, HealthProfile, ActivityLog, WorkoutPlan, FoodItem, Recommendation, Reminder, Trainer, Doctor
│   ├── controllers/     (13)   # Business logic for all features
│   ├── routes/          (13)   # Flask Blueprints → 22 API endpoints
│   ├── schemas/         (5)    # Marshmallow validation (auth, profile, activity, reminder, workout)
│   ├── middleware/       (2)   # JWT auth decorator + validation decorator
│   ├── utils/           (7)    # BMI calculator, recommendation engine, diet/workout templates, PDF generator, validators, quote generator
│   ├── migrations/             # Flask-Migrate (Alembic)
│   ├── seed_food_data.py       # 50+ Indian & international food items
│   └── seed_trainers_doctors.py # 7 trainers + 6 doctors (Indian data)
│
└── frontend/                   # Static HTML/CSS/JS (served on port 3000)
    ├── index.html              # Login page
    ├── register.html           # Register page
    ├── dashboard.html          # Main dashboard (charts, stats, quote)
    ├── profile.html            # Health profile form + PDF export
    ├── tracker.html            # Activity logger (meal/workout/water/sleep)
    ├── recommendations.html    # AI diet + workout recommendations
    ├── food-scanner.html       # Food search + barcode scanner
    ├── workout.html            # Workout planner + exercise timer
    ├── progress.html           # Progress charts (weekly/monthly)
    ├── trainers.html           # Trainer directory
    ├── doctors.html            # Doctor directory
    ├── ai-planner.html         # AI chat (voice input/output)
    ├── reminders.html          # Reminder management + browser notifications
    ├── js/              (19)   # All JavaScript modules
    ├── css/              (8)   # All stylesheets
    └── frontend_api_contract.md # Complete 22-endpoint API contract
```

## Key Documents

| Document | Path | Description |
|----------|------|-------------|
| **Project Status Report** | `C:\Users\rajus\.gemini\antigravity\brain\853caaf8-1996-432d-88c0-bc96b22fa74d\FitLife_Project_Status.md` | Comprehensive report of everything done and everything pending. Includes every file, every endpoint, every model, every controller with clickable links. |
| **API Contract** | `frontend/frontend_api_contract.md` | Full 22-endpoint REST API contract with request/response schemas, enums, error formats |
| **Backend Plan** | `backend/BACKEND_PLAN.md` | Detailed backend implementation plan (~58 KB) |
| **Frontend Plan** | `frontend/FRONTEND_PLAN.md` | Detailed frontend implementation plan (~47 KB) |
| **Project Blueprint** | `backend/AI_FitnessApp_Blueprint.md` | Original full project blueprint (~38 KB) |
| **Backend README** | `backend/README.md` | Quick start guide, endpoint table, tech stack |

## Current Status (as of March 31, 2026)

### ✅ Complete (~85%)
- All 9 database models with relationships and cascade deletes
- All 13 controllers with full business logic
- All 22 REST API endpoints across 13 route blueprints
- 5 Marshmallow validation schemas
- JWT authentication + middleware
- Rate limiting on auth + AI + export endpoints
- BMI/BMR/TDEE/calorie calculation engine (Mifflin-St Jeor)
- Rule-based recommendation engine (15 diet plans × 3 workout plans)
- PDF health report generator (fpdf2)
- Groq AI integration with personalized context + fallback responses
- Seed data: 50+ foods, 7 trainers, 6 doctors
- Full frontend: 12 pages, 19 JS modules, 8 CSS files
- Dark mode, animations, glassmorphism design
- API contract documentation

### ⚠️ Pending
- **Database Setup:** MySQL DB creation + migrations + seed data (manual steps)
- **Groq API Key:** Required for AI chat (has keyword-based fallback)
- **Automated Testing:** 0% done — pytest in deps but no test files
- **Security:** Default secrets, no password reset, no email verification
- **Deployment:** No production config/hosting/SSL
- **Nice-to-haves:** Weight history table, activity edit/delete, APScheduler jobs, PWA, admin panel

## Tech Stack
- **Backend:** Python 3.11+, Flask 3.0, SQLAlchemy, Flask-Migrate, PyMySQL, Flask-JWT-Extended, Flask-Bcrypt, Marshmallow, Flask-Limiter, Groq SDK, fpdf2, APScheduler
- **Frontend:** Vanilla HTML5, CSS3 (custom properties, glassmorphism), JavaScript (ES6+), Chart.js, Web Speech API
- **Database:** MySQL 8.0 (utf8mb4)
- **AI:** Groq API with Llama 3 70B model (free tier)

## API Quick Reference (22 Endpoints)

| # | Method | Endpoint | Auth |
|---|--------|----------|------|
| 1 | POST | `/api/register` | ❌ |
| 2 | POST | `/api/login` | ❌ |
| 3 | POST | `/api/logout` | ❌ |
| 4 | GET | `/api/profile` | ✅ |
| 5 | POST | `/api/profile` | ✅ |
| 6 | GET | `/api/dashboard` | ✅ |
| 7 | GET | `/api/recommendations` | ✅ |
| 8 | POST | `/api/activity` | ✅ |
| 9 | GET | `/api/activity` | ✅ |
| 10 | GET | `/api/food/search` | ✅ |
| 11 | POST | `/api/food/scan` | ✅ |
| 12 | GET | `/api/workout/plan` | ✅ |
| 13 | POST | `/api/workout/plan` | ✅ |
| 14 | POST | `/api/workout/timer` | ✅ |
| 15 | GET | `/api/trainers` | ✅ |
| 16 | GET | `/api/doctors` | ✅ |
| 17 | POST | `/api/ai/diet-chat` | ✅ |
| 18 | GET | `/api/reminders` | ✅ |
| 19 | POST | `/api/reminders` | ✅ |
| 20 | DELETE | `/api/reminders/<id>` | ✅ |
| 21 | GET | `/api/progress` | ✅ |
| 22 | GET | `/api/export/pdf` | ✅ |

## Conversation History

- **Conversation 853caaf8**: Created the detailed `FitLife_Project_Status.md` document covering all done & pending work
- **Conversation 9ddd922b**: Built frontend authentication (login/register pages)
- **Conversation d092ca1c**: Implemented frontend pages (tracker, recommendations, workout, food scanner, AI planner)
- **Conversation 4fb095f6**: Created the initial implementation plan and resolved API contract discrepancies
