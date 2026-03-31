# 🏋️ FitLife Backend — AI Fitness Management System

> Python 3.11+ · Flask · MySQL · JWT · Groq AI (Llama 3) · REST API

## Quick Start

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database
```bash
mysql -u root -p
```
```sql
CREATE DATABASE fitness_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 4. Configure Environment
```bash
# .env file is already configured. Verify your MySQL password is correct.
```

### 5. Run Database Migrations
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Seed Sample Data
```bash
python seed_food_data.py
python seed_trainers_doctors.py
```

### 7. Start the Server
```bash
python app.py
```
- Server: http://localhost:5000
- Health Check: http://localhost:5000/health

---

## API Endpoints (22 Total)

| # | Method | Endpoint | Auth | Description |
|---|--------|----------|------|-------------|
| 1 | POST | `/api/register` | ❌ | Register user |
| 2 | POST | `/api/login` | ❌ | Login, get JWT |
| 3 | POST | `/api/logout` | ❌ | Logout |
| 4 | GET | `/api/profile` | ✅ | Get health profile |
| 5 | POST | `/api/profile` | ✅ | Create/update profile |
| 6 | GET | `/api/dashboard` | ✅ | Dashboard summary |
| 7 | GET | `/api/recommendations` | ✅ | Diet + workout recs |
| 8 | POST | `/api/activity` | ✅ | Log activity |
| 9 | GET | `/api/activity` | ✅ | Get logs by date |
| 10 | GET | `/api/food/search` | ✅ | Search food DB |
| 11 | POST | `/api/food/scan` | ✅ | Barcode lookup |
| 12 | GET | `/api/workout/plan` | ✅ | Get workout plan |
| 13 | POST | `/api/workout/plan` | ✅ | Save workout plan |
| 14 | POST | `/api/workout/timer` | ✅ | Log timer session |
| 15 | GET | `/api/trainers` | ✅ | List trainers |
| 16 | GET | `/api/doctors` | ✅ | List doctors |
| 17 | POST | `/api/ai/diet-chat` | ✅ | AI diet assistant |
| 18 | GET | `/api/reminders` | ✅ | List reminders |
| 19 | POST | `/api/reminders` | ✅ | Create reminder |
| 20 | DELETE | `/api/reminders/<id>` | ✅ | Delete reminder |
| 21 | GET | `/api/progress` | ✅ | Progress data |
| 22 | GET | `/api/export/pdf` | ✅ | Download PDF report |

---

## Project Structure

```
backend/
├── app.py                    # Flask app factory
├── config.py                 # Dev/Prod configuration
├── extensions.py             # Shared Flask extensions
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (gitignored)
├── models/          (10)     # SQLAlchemy models
├── schemas/         (6)      # Marshmallow validation
├── middleware/      (3)      # JWT auth + validation decorators
├── utils/           (8)      # BMI calc, recommendation engine, PDF, etc.
├── controllers/     (14)     # Business logic
├── routes/          (14)     # Flask Blueprints
├── seed_food_data.py         # 50+ Indian food items
└── seed_trainers_doctors.py  # 7 trainers + 6 doctors
```

## Tech Stack
- **Framework:** Flask 3.0
- **Database:** MySQL 8.0 + SQLAlchemy + Flask-Migrate
- **Auth:** JWT (Flask-JWT-Extended) + bcrypt
- **AI:** Groq API (Llama 3 70B) — FREE
- **PDF:** fpdf2 (pure Python)
- **Validation:** Marshmallow
- **Rate Limiting:** Flask-Limiter
- **Scheduler:** APScheduler
