"""Generate a project-overview PDF for the FitLife backend."""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fpdf import FPDF


OUTPUT_PATH = ROOT_DIR / "docs" / "FitLife_Project_Overview.pdf"


SECTIONS = [
    (
        "Project Ideology",
        [
            "FitLife is designed as an AI-assisted fitness companion, not just a calorie logger.",
            "The product combines health profile analysis, food intelligence, adaptive workout planning, and progress tracking into one user journey.",
            "The core idea is personalization: every major module reacts to the user's goal, body metrics, lifestyle, and activity history."
        ]
    ),
    (
        "Backend Tech Stack",
        [
            "Framework: Flask 3 with an application-factory structure.",
            "Database: PostgreSQL on Neon, accessed through SQLAlchemy and Flask-Migrate.",
            "Authentication: JWT-based auth with bcrypt password hashing.",
            "Validation and API shaping: Marshmallow schemas and route/controller separation.",
            "AI integrations: Groq and Gemini-compatible scanner paths, plus rule-based and model-backed recommendation logic.",
            "PDF and reporting: fpdf2 for exportable health and project documents.",
            "Scheduling and limits: APScheduler and Flask-Limiter."
        ]
    ),
    (
        "Current Backend Architecture",
        [
            "Routes expose REST endpoints for auth, profile, dashboard, activity logging, food scanning, recommendations, workouts, reminders, trainers, doctors, exports, and progress.",
            "Controllers keep business logic separate from route definitions.",
            "Models represent users, health profiles, recommendations, activity logs, foods, workout plans, reminders, and the new advanced workout data tables.",
            "Utility modules handle calculations, food intelligence, recommendation logic, PDF generation, body-fat estimation, goal timeline estimation, and adaptive workout planning."
        ]
    ),
    (
        "Advanced Workout System",
        [
            "A large exercise library is imported from the free-exercise-db dataset and stored in the backend for real plan generation.",
            "The system now uses 800+ exercises with media URLs, instructions, muscle groups, levels, and categories.",
            "BMI and BFP reference datasets are used to estimate a realistic goal period and select an appropriate workout intensity band.",
            "Workout plans are generated dynamically from the user's fitness goal, BMI, body-fat percentage, activity level, and active-day capacity.",
            "The planner returns a hero section, a predicted goal-achievement period, daily exercise blocks, timer metadata, calories burned, and active session state."
        ]
    ),
    (
        "Machine-Learning Style Goal Estimation",
        [
            "The current model layer uses dataset-backed similarity and heuristic estimation rather than a heavy standalone training pipeline.",
            "It matches the user's profile against historical BMI/BFP reference rows and computes a plan-code, focus area, target body metrics, and estimated weeks to goal.",
            "This gives the capstone project a stronger data-driven story: the workout plan is selected from both live profile values and reference-driven estimation."
        ]
    ),
    (
        "Food and Recommendation Workflow",
        [
            "The scanner combines AI vision, fallback catalog matching, nutrition shaping, and goal-based warnings.",
            "Recommendations merge diet templates, calculated calorie targets, and workout outputs from the planner.",
            "Dashboard and progress endpoints aggregate health profile, recommendation state, and real user activity logs to reflect the user's current journey."
        ]
    ),
    (
        "Workflow Summary",
        [
            "1. User registers and logs in.",
            "2. User creates or updates a health profile.",
            "3. Backend recalculates BMI, BMR, calories, body-fat estimates, and recommendation state.",
            "4. Adaptive workout plan is generated using the exercise library plus the goal-period estimator.",
            "5. Frontend displays today's workout, estimated timeline, timer controls, and media-backed exercises.",
            "6. User logs meals, workouts, water, and sleep; dashboard and progress update from live data."
        ]
    ),
    (
        "Major Capstone Highlights",
        [
            "Adaptive workout planning driven by user biometrics.",
            "Reference-dataset-backed goal period estimation.",
            "Large structured exercise library with media-backed exercises.",
            "AI food scanner with fallback and goal-fit warnings.",
            "JWT-secured multi-module backend with reporting and progress tracking.",
            "Architecture that cleanly separates models, controllers, routes, utilities, and data import pipelines."
        ]
    ),
]


class ProjectPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 212, 170)
        self.rect(0, 0, 210, 26, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 20)
        self.set_y(8)
        self.cell(0, 10, "FitLife Project Overview", align="C")
        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"FitLife Backend Brief - Page {self.page_no()}", align="C")


def build_pdf():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    pdf = ProjectPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_text_color(35, 35, 50)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Capstone Backend Brief", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        7,
        "This document summarizes the ideology, architecture, tech stack, workflow, and major capstone-grade features of the current FitLife backend."
    )
    pdf.ln(3)

    for title, bullets in SECTIONS:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(0, 110, 98)
        pdf.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(35, 35, 50)
        pdf.set_font("Helvetica", "", 10.5)
        for bullet in bullets:
            pdf.set_x(14)
            pdf.cell(4, 6.5, "-")
            pdf.multi_cell(0, 6.5, bullet)
        pdf.ln(2)

    pdf.output(str(OUTPUT_PATH))
    print(str(OUTPUT_PATH))


if __name__ == "__main__":
    build_pdf()
