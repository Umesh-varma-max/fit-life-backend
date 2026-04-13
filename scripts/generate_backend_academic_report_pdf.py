"""Generate an academic-style backend capstone PDF report."""

from __future__ import annotations

from pathlib import Path
import sys

from fpdf import FPDF


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUTPUT_PATH = ROOT_DIR / "docs" / "FitLife_Backend_Academic_Report.pdf"


def pdf_safe(text: str) -> str:
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u2026": "...",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


SECTIONS = [
    (
        "Abstract",
        [
            "FitLife is a backend-driven intelligent fitness platform developed as a capstone project to support personalized nutrition, workout planning, health tracking, AI-assisted food analysis, and progress reporting. The backend is designed as the core decision-making layer of the application. It collects health metrics, processes user activity, computes body indicators such as BMI, BMR, TDEE, and estimated body-fat percentage, and produces tailored outputs such as calorie targets, diet recommendations, adaptive workout plans, and progress summaries.",
            "The project demonstrates how a modular Flask backend can combine secure REST APIs, PostgreSQL persistence, rule-based analytics, dataset-backed estimation, and AI-assisted features into one integrated system. From an academic perspective, the backend contributes not only basic application functionality, but also a structured personalization pipeline and a data-informed workout generation approach that raises the project beyond a standard CRUD application."
        ],
    ),
    (
        "1. Introduction",
        [
            "Modern fitness applications often provide fragmented services such as calorie logging, exercise tracking, or simple recommendations. Many of them do not meaningfully adapt to individual body metrics, lifestyle, or progress. FitLife addresses this gap by building a backend that acts as an intelligence layer for the user journey. The objective is not simply to store data, but to interpret data and convert it into practical, personalized decisions.",
            "The backend is responsible for authentication, profile management, nutrition intelligence, workout planning, dashboard analytics, progress monitoring, reminder management, care-provider discovery, and report export. It also supports AI-driven features such as a food scanner and an in-app health planner. This makes the backend the most academically significant part of the project, because it integrates system design, database modeling, applied health logic, and AI-assisted computation."
        ],
    ),
    (
        "2. Project Objectives",
        [
            "The first objective of the backend is to create a secure and modular service layer that can support all major frontend features through clean API contracts.",
            "The second objective is personalization: user-specific profile data should influence calorie calculations, recommendation generation, and workout planning.",
            "The third objective is to demonstrate data-informed intelligence by using imported BMI/BFP reference datasets and a large exercise library to enrich planning quality.",
            "The fourth objective is to provide capstone-grade features such as AI-assisted food analysis, image persistence, PDF reporting, progress dashboards, and session-aware workout execution."
        ],
    ),
    (
        "3. Backend Architecture",
        [
            "The backend follows a Flask application-factory architecture centered on app.py. This design separates application creation from runtime execution, which improves modularity, deployment flexibility, and maintainability.",
            "The overall architecture is layered. Routes define endpoint boundaries, middleware handles authentication and validation, controllers contain business logic, models manage persistent entities, and utility modules implement calculations, recommendation logic, AI wrappers, planning algorithms, and report generation.",
            "This architecture is academically valuable because it demonstrates separation of concerns, reusability, and scalable design rather than tightly coupled logic."
        ],
    ),
    (
        "4. Core Technology Stack",
        [
            "The backend uses Flask 3 as the primary web framework for API construction. SQLAlchemy is used as the ORM to map application objects to PostgreSQL tables. Flask-Migrate is used to manage schema evolution. PostgreSQL, typically accessed through Neon-hosted DATABASE_URL configuration, is the primary persistence layer.",
            "Authentication is implemented using Flask-JWT-Extended and password hashing is handled through Flask-Bcrypt. Marshmallow is used for structured request validation. Flask-CORS enables controlled frontend access. Flask-Limiter provides rate limiting. APScheduler is included for scheduling-oriented features. requests is used for outbound HTTP integration. fpdf2 is used for PDF generation.",
            "The stack is suitable for a capstone because it demonstrates full-stack backend competency: API development, persistence, security, validation, deployment, and reporting."
        ],
    ),
    (
        "5. Functional Modules",
        [
            "Authentication module: handles user registration, login, JWT issuance, and secure access control for protected routes.",
            "Health profile module: collects age, gender, height, weight, activity level, sleep habits, food habits, and fitness goal. It computes derived indicators such as BMI, BMR, TDEE, daily calories, and estimated body-fat percentage.",
            "Dashboard module: aggregates current-day and recent data into user-facing summaries such as calories in, calories out, hydration, streaks, and weekly chart metrics.",
            "Activity module: records meals, workouts, water intake, sleep logs, and image-backed meal entries.",
            "Food intelligence module: supports search, scan, image analysis, nutrition shaping, fallback matching, and goal-aware food warnings.",
            "Workout module: produces either custom plans or adaptive profile-driven plans, supports timer logging, and manages workout sessions.",
            "Recommendation module: generates diet and workout recommendations from profile state and planner logic.",
            "AI planner module: answers user health questions using profile, workout, and activity context.",
            "Progress module: builds trend summaries suitable for charts and progress visualization.",
            "Reminder, trainer, doctor, and export modules provide supporting application features that improve completeness and real-world usability."
        ],
    ),
    (
        "6. Data Model Design",
        [
            "The backend uses relational data modeling to represent the user journey. The User model stores authentication identity. HealthProfile stores the user's body metrics and fitness context. ActivityLog stores meals, workouts, hydration, sleep, and scanned images. Recommendation stores generated diet and workout recommendation payloads. WorkoutPlan stores custom day-specific plans. WorkoutSession stores state for timer-driven session execution. FoodItem stores nutrition records for search and fallback matching. Reminder stores reminder definitions. Trainer and Doctor store provider-directory data.",
            "Two academically important models extend the intelligence of the system. ExerciseLibrary stores imported exercise data, including names, muscle groups, equipment, instructions, and image/demo media. BodyMetricReference stores reference rows from BMI and BFP datasets used by the goal-estimation logic.",
            "This modeling approach shows that the backend is not only transactional, but also knowledge-backed."
        ],
    ),
    (
        "7. Health Computation Pipeline",
        [
            "When a user submits a health profile, the backend performs a sequence of computations. BMI is calculated from height and weight. BMI category is derived from standard ranges. BMR is calculated using the Mifflin-St Jeor equation. TDEE is derived by multiplying BMR with an activity multiplier. Daily calorie targets are adjusted according to the fitness goal. Estimated body-fat percentage is computed using a practical heuristic from body_fat.py, and a body-fat category is then assigned.",
            "These calculations are central to personalization. Instead of storing only raw values, the backend transforms them into meaningful indicators that influence recommendations, AI responses, and workout planning."
        ],
    ),
    (
        "8. Recommendation Logic",
        [
            "The recommendation engine combines body metrics, calorie targets, food habits, and workout planning outputs. It produces diet-plan suggestions and a workout recommendation structure. The recommendation controller also supports legacy frontend expectations while enriching the response with newer planning metadata such as hero image, body-fat category, and goal-estimated weeks.",
            "This hybrid design is useful academically because it demonstrates backward compatibility alongside progressive feature evolution."
        ],
    ),
    (
        "9. Adaptive Workout Planning",
        [
            "The workout subsystem is one of the strongest backend contributions. It no longer relies only on static templates. Instead, it imports a large exercise library and combines it with a goal-estimation model to create profile-driven plans.",
            "The planner first estimates a user's target metrics and goal-achievement period. It then selects a weekly goal track according to weight loss, muscle gain, or maintenance. Exercises are scored using category relevance, primary and secondary muscle overlap, difficulty fit, and media availability. Selected exercises are then prescribed with sets, reps, duration, rest periods, and estimated calories burned.",
            "The result is a structured day-wise plan that includes a current-day workout, weekly schedule, estimated total minutes, calories burned, goal label, goal badge, confidence level, and timeline to goal."
        ],
    ),
    (
        "10. Dataset-Backed Goal Estimation",
        [
            "A particularly strong capstone element is the lightweight model-backed estimator implemented in goal_achievement_model.py. The backend imports BMI and body-fat reference datasets, stores them in BodyMetricReference, and uses them as comparison anchors.",
            "For each user profile, the backend computes candidate distance against reference rows using BMI, age, and body-fat difference. It then estimates target BMI, target body-fat percentage, safe weekly change rate, goal period in weeks, and a plan code/focus value. The estimator blends heuristic calculations with similarity-based reference matching.",
            "Although this is not a heavyweight machine learning pipeline with separate training and inference infrastructure, it is still academically valuable because it demonstrates data-driven estimation rather than purely hardcoded planning."
        ],
    ),
    (
        "11. Exercise Library Integration",
        [
            "The backend supports importing exercise content from the free-exercise-db dataset. Imported records include exercise identity, level, category, muscle groups, instructions, and image/demo URLs. This significantly improves the quality of the workout feature because the planner can return actual media-backed exercises instead of generic names.",
            "In academic terms, this transforms the workout feature from a static demonstration into a data-enriched recommendation system."
        ],
    ),
    (
        "12. Food Scanner and Nutrition Intelligence",
        [
            "The food scanner supports image analysis, nutrition estimation, fallback catalog matching, and goal-based warning generation. The logic is implemented in the food controller and AI helper utilities. The scanner validates file size and MIME type, attempts structured AI recognition, enriches output using the local food database, and falls back to keyword-based catalog matching when vision confidence is weak.",
            "A notable engineering feature is persistence of scan images. When a meal is logged from a food scan, the backend stores the uploaded image bytes and exposes them through a protected endpoint. This allows scan history to work across devices and accounts instead of relying on browser-only thumbnails."
        ],
    ),
    (
        "13. AI Planner Module",
        [
            "The AI planner is not implemented as a generic chatbot. It is context-aware. It first detects the message topic, then loads only the relevant profile, recommendation, workout, and activity context. It uses this information to build a personalized system prompt for the model. If AI inference fails, it still returns a rule-based, profile-aware fallback response.",
            "This design is academically meaningful because it shows orchestration of domain context around model usage rather than naive prompt forwarding."
        ],
    ),
    (
        "14. Dashboard, Progress, and Reporting",
        [
            "The dashboard controller aggregates current-day and weekly activity into user-readable metrics such as calories consumed, calories burned, hydration, streak, and motivation. The progress controller prepares trend-oriented summaries suitable for weekly or monthly charting. The export controller turns recent profile and activity information into a PDF health report.",
            "This layer shows the backend's analytical role. It does not merely return rows from the database; it transforms user history into informative summaries."
        ],
    ),
    (
        "15. Security, Validation, and Reliability",
        [
            "The backend enforces input validation with Marshmallow schemas and route decorators. Passwords are hashed with bcrypt. JWT tokens secure protected resources. CORS is restricted to configured frontend origins. Rate limiting reduces abuse risk. Standardized JSON error handling improves client predictability.",
            "The use of middleware for both authentication and validation strengthens maintainability and makes the system easier to reason about academically."
        ],
    ),
    (
        "16. Setup and Deployment Workflow",
        [
            "The repository includes local development and cloud deployment support. The backend can run locally through app.py and is deployed to Render through render.yaml using Gunicorn and wsgi.py. Configuration is controlled through environment variables such as DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, FRONTEND_ORIGIN, GROQ_API_KEY, and related runtime settings.",
            "This demonstrates deployment awareness, which is an important capstone expectation."
        ],
    ),
    (
        "17. Assumptions, Limitations, and Edge Cases",
        [
            "Estimated body-fat percentage is heuristic and not clinically measured. Goal-period estimation is data-informed and heuristic rather than a separately trained predictive model. Scanner performance depends on AI provider availability, region support, image clarity, and fallback catalog coverage. Some repository documentation files are older than the newest backend enhancements. The repository does not currently contain a large automated testing suite.",
            "Despite these limitations, the system still demonstrates strong backend engineering maturity because it handles many edge cases explicitly. Missing profiles, invalid JWTs, unclear food photos, absent active sessions, custom-plan overrides, and missing request context for image URLs are all addressed in code."
        ],
    ),
    (
        "18. Capstone Significance",
        [
            "The backend qualifies as capstone-level work because it integrates secure API design, relational data modeling, health computation, personalization logic, dataset-backed estimation, AI-assisted nutrition support, adaptive workout generation, session tracking, and report export into a single coherent system.",
            "Its strongest academic contributions are the adaptive workout engine, the dataset-backed goal-period estimator, the context-aware AI planner, and the image-persistent food scan history. Together, these features elevate the project beyond a standard fitness tracker and position it as an intelligent decision-support platform."
        ],
    ),
    (
        "19. Conclusion",
        [
            "From the backend perspective, FitLife is a complete applied software engineering project with strong academic depth. It demonstrates practical health analytics, personalized decision logic, database design, secure API development, AI integration, and deployable architecture. The backend is the foundation that gives the project research and capstone value because it turns profile and activity data into meaningful, individualized outputs.",
            "In summary, the backend is not just supporting the frontend. It is the computational brain of the project."
        ],
    ),
]


class AcademicPDF(FPDF):
    def header(self):
        self.set_fill_color(20, 184, 166)
        self.rect(0, 0, 210, 22, "F")
        self.set_y(6)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 10, pdf_safe("FitLife Backend Academic Report"), align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-10)
        self.set_text_color(110, 110, 110)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 6, pdf_safe(f"FitLife Backend Research Report - Page {self.page_no()}"), align="C")

    def section_title(self, text: str):
        self.set_text_color(8, 100, 90)
        self.set_font("Helvetica", "B", 13)
        self.set_x(self.l_margin)
        self.cell(0, 8, pdf_safe(text), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(30, 30, 40)

    def paragraph(self, text: str):
        self.set_font("Helvetica", "", 10.5)
        self.set_x(self.l_margin)
        self.multi_cell(0, 6, pdf_safe(text))
        self.ln(1)


def build_pdf() -> Path:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf = AcademicPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(35, 35, 45)
    pdf.cell(0, 12, pdf_safe("Backend Academic Research Report"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        7,
        pdf_safe(
            "This report presents the backend of FitLife as an academic capstone system. "
            "It focuses only on the backend engineering, data, architecture, workflows, and research value."
        ),
    )
    pdf.ln(2)

    for title, paragraphs in SECTIONS:
        pdf.section_title(title)
        for paragraph in paragraphs:
            pdf.paragraph(paragraph)

    pdf.output(str(OUTPUT_PATH))
    return OUTPUT_PATH


if __name__ == "__main__":
    print(build_pdf())
