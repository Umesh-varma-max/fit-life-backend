"""Generate a comprehensive backend technical manual PDF from repository analysis."""

from __future__ import annotations

import ast
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from fpdf import FPDF


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

OUTPUT_PATH = ROOT_DIR / "docs" / "FitLife_Backend_Technical_Manual.pdf"
TARGET_DIRS = ["controllers", "routes", "models", "utils", "schemas", "middleware", "scripts"]
TOP_LEVEL_FILES = ["app.py", "wsgi.py", "config.py", "extensions.py", "README.md", "render.yaml", "requirements.txt"]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def summarize_text(text: str, fallback: str) -> str:
    clean = re.sub(r"\s+", " ", (text or "").strip())
    return clean if clean else fallback


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


def is_sqlalchemy_field(value: ast.AST) -> bool:
    return isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr in {"Column", "relationship"}


def parse_class(node: ast.ClassDef) -> dict[str, Any]:
    fields: list[str] = []
    methods: list[str] = []
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and is_sqlalchemy_field(item.value):
                    fields.append(target.id)
        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and not item.name.startswith("_"):
            methods.append(item.name)
    return {"name": node.name, "doc": ast.get_docstring(node), "fields": fields, "methods": methods}


def parse_route_decorators(node: ast.FunctionDef | ast.AsyncFunctionDef, prefixes: dict[str, str]) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for deco in node.decorator_list:
        if not isinstance(deco, ast.Call) or not isinstance(deco.func, ast.Attribute):
            continue
        if deco.func.attr not in {"route", "get", "post", "put", "delete", "patch"}:
            continue
        if not isinstance(deco.func.value, ast.Name):
            continue

        path = ""
        if deco.args and isinstance(deco.args[0], ast.Constant):
            path = str(deco.args[0].value)

        methods: list[str] = []
        for keyword in deco.keywords:
            if keyword.arg == "methods" and isinstance(keyword.value, (ast.List, ast.Tuple)):
                methods = [str(item.value) for item in keyword.value.elts if isinstance(item, ast.Constant)]
        if not methods:
            methods = [deco.func.attr.upper()] if deco.func.attr != "route" else ["GET"]

        routes.append(
            {
                "function": node.name,
                "path": f"{prefixes.get(deco.func.value.id, '')}{path}",
                "methods": methods,
                "doc": ast.get_docstring(node),
            }
        )
    return routes


def scan_python_file(path: Path) -> dict[str, Any]:
    source = read_text(path)
    tree = ast.parse(source)

    imports: list[str] = []
    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    env_vars: set[str] = set()
    prefixes: dict[str, str] = {}

    for match in re.finditer(r"os\.getenv\(\s*['\"]([^'\"]+)['\"]", source):
        env_vars.add(match.group(1))

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(f"{node.module or ''}:{','.join(alias.name for alias in node.names)}")
        elif isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "Blueprint":
                prefix = ""
                for keyword in node.value.keywords:
                    if keyword.arg == "url_prefix" and isinstance(keyword.value, ast.Constant):
                        prefix = str(keyword.value.value)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        prefixes[target.id] = prefix
        elif isinstance(node, ast.ClassDef):
            classes.append(parse_class(node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({"name": node.name, "doc": ast.get_docstring(node)})

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            routes.extend(parse_route_decorators(node, prefixes))

    return {
        "path": path,
        "relative_path": str(path.relative_to(ROOT_DIR)),
        "doc": ast.get_docstring(tree),
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "routes": routes,
        "env_vars": sorted(env_vars),
        "line_count": len(source.splitlines()),
    }


def parse_requirements(path: Path) -> list[dict[str, str]]:
    deps: list[dict[str, str]] = []
    current_group = "General"
    if not path.exists():
        return deps
    for raw_line in read_text(path).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            current_group = line.lstrip("#").strip()
            continue
        if "==" in line:
            name, version = line.split("==", 1)
        else:
            name, version = line, ""
        deps.append({"group": current_group, "name": name.strip(), "version": version.strip()})
    return deps


def dataset_rows() -> dict[str, int]:
    counts: dict[str, int] = {}
    for filename in ["final_dataset.csv", "final_dataset_BFP.csv"]:
        path = ROOT_DIR / "data" / filename
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            counts[filename] = max(sum(1 for _ in csv.reader(handle)) - 1, 0)
    return counts


def scan_repository() -> dict[str, Any]:
    data: dict[str, Any] = {"python_files": [], "dirs": defaultdict(list), "env_vars": set()}
    for folder in TARGET_DIRS:
        for path in sorted((ROOT_DIR / folder).glob("*.py")):
            if path.name == "__init__.py":
                continue
            info = scan_python_file(path)
            data["python_files"].append(info)
            data["dirs"][folder].append(info)
            data["env_vars"].update(info["env_vars"])
    data["top_files"] = {name: read_text(ROOT_DIR / name) for name in TOP_LEVEL_FILES if (ROOT_DIR / name).exists()}
    data["requirements"] = parse_requirements(ROOT_DIR / "requirements.txt")
    data["route_inventory"] = sorted([route for item in data["python_files"] for route in item["routes"]], key=lambda item: item["path"])
    data["model_inventory"] = list(data["dirs"]["models"])
    data["counts"] = {folder: len(data["dirs"][folder]) for folder in TARGET_DIRS}
    data["counts"]["python_files"] = len(data["python_files"])
    data["dataset_rows"] = dataset_rows()
    return data


class ManualPDF(FPDF):
    def header(self):
        self.set_fill_color(12, 202, 180)
        self.rect(0, 0, 210, 22, "F")
        self.set_y(6)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 18)
        self.cell(0, 10, pdf_safe("FitLife Backend Technical Manual"), align="C")
        self.ln(12)

    def footer(self):
        self.set_y(-10)
        self.set_text_color(110, 110, 110)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 6, pdf_safe(f"Generated from repository analysis - Page {self.page_no()}"), align="C")

    def section_title(self, title: str):
        self.set_text_color(10, 120, 110)
        self.set_font("Helvetica", "B", 14)
        self.ln(2)
        self.cell(0, 8, pdf_safe(title), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(35, 35, 45)

    def body(self, text: str, size: float = 10.5):
        self.set_font("Helvetica", "", size)
        self.set_x(self.l_margin)
        self.multi_cell(0, 6, pdf_safe(text))

    def bullet(self, text: str, size: float = 10):
        self.set_font("Helvetica", "", size)
        self.set_x(self.l_margin)
        self.multi_cell(0, 6, pdf_safe(f"- {text}"))

    def mono_block(self, text: str):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(245, 248, 250)
        self.set_x(self.l_margin)
        self.multi_cell(0, 4.5, pdf_safe(text), border=1, fill=True)
        self.set_font("Helvetica", "", 10)


def add_cover(pdf: ManualPDF, data: dict[str, Any]):
    pdf.set_text_color(35, 35, 45)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, pdf_safe("Comprehensive Backend Documentation"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        7,
        pdf_safe(
            "This manual is produced by scanning the current repository structure, route definitions, controllers, utilities, deployment files, and bundled datasets. "
            "It documents the backend as implemented in code."
        )
    )
    pdf.ln(3)
    pdf.bullet(f"Repository root: {ROOT_DIR}")
    pdf.bullet(f"Python source files analyzed: {data['counts']['python_files']}")
    pdf.bullet(
        "Layer counts: "
        f"{data['counts']['controllers']} controllers, "
        f"{data['counts']['routes']} route modules, "
        f"{data['counts']['models']} models, "
        f"{data['counts']['utils']} utility modules, "
        f"{data['counts']['schemas']} schemas."
    )
    for name, count in data["dataset_rows"].items():
        pdf.bullet(f"Bundled dataset: {name} with {count} data rows")


def add_project_overview(pdf: ManualPDF):
    pdf.section_title("1. Project Purpose, Goals, and Scope")
    pdf.body(
        "FitLife is a health, nutrition, and fitness backend that supports user authentication, health-profile capture, adaptive recommendations, AI-assisted food scanning, "
        "dashboard aggregation, progress tracking, reminder management, PDF export, and adaptive workout planning."
    )
    pdf.body(
        "The central product idea is personalization. Age, gender, height, weight, activity level, food habits, BMI, estimated body-fat percentage, and fitness goal all influence "
        "calorie targets, recommendation content, AI planner responses, and workout-plan generation."
    )
    pdf.bullet("Primary domains: authentication, health profiling, activity logging, food intelligence, workout planning, reminders, progress, recommendations, exports, and provider directories.")
    pdf.bullet("Advanced capstone features in the repository include dataset-backed goal-period estimation, imported exercise media, workout sessions, and persisted scan images.")


def add_architecture(pdf: ManualPDF):
    pdf.section_title("2. Architecture and Layering")
    pdf.body(
        "The backend follows a standard Flask application-factory architecture with a thin route layer, controller-driven business logic, SQLAlchemy models, utility modules for algorithms and AI integration, "
        "and Marshmallow schemas for request validation."
    )
    pdf.mono_block(
        "Client / Frontend\n"
        "    |\n"
        "    v\n"
        "Flask Blueprint Route -> Validation Middleware -> JWT Middleware -> Controller\n"
        "    |\n"
        "    +--> SQLAlchemy Models / PostgreSQL\n"
        "    +--> Utility Modules (calculators, AI, planners, PDF generation)\n"
        "    +--> JSON / PDF / Image Response"
    )
    pdf.bullet("Entry point: app.py creates the app, loads config, initializes extensions, registers blueprints, and defines global error handlers plus /health.")
    pdf.bullet("WSGI entry: wsgi.py exposes create_app('production') for Gunicorn and Render.")
    pdf.bullet("Configuration: config.py resolves DB URI, secrets, CORS origins, and API integration keys.")
    pdf.bullet("Extensions: extensions.py centralizes SQLAlchemy, JWT, bcrypt, CORS, migrations, rate limiting, and APScheduler.")


def add_setup(pdf: ManualPDF, data: dict[str, Any]):
    pdf.section_title("3. Setup, Configuration, and Deployment")
    pdf.body("Deployment and setup details were verified from README.md, config.py, render.yaml, and wsgi.py.")
    pdf.bullet("Install dependencies: pip install -r requirements.txt")
    pdf.bullet("Local run path documented in README: python app.py")
    pdf.bullet("Production start command from render.yaml: gunicorn wsgi:app")
    pdf.bullet("Health endpoint: /health")
    pdf.body("Environment variables discovered directly from code:")
    explanations = {
        "DATABASE_URL": "Primary PostgreSQL/Neon connection string.",
        "DB_DIALECT": "Fallback database dialect when DATABASE_URL is missing.",
        "DB_HOST": "Fallback database host.",
        "DB_PORT": "Fallback database port.",
        "DB_NAME": "Fallback database name.",
        "DB_USER": "Fallback database username.",
        "DB_PASSWORD": "Fallback database password.",
        "SECRET_KEY": "Flask application secret.",
        "JWT_SECRET_KEY": "JWT signing secret.",
        "FLASK_ENV": "Switches development or production config.",
        "FRONTEND_ORIGIN": "Allowed CORS origins, optionally comma-separated.",
        "GROQ_API_KEY": "Groq API key used by chatbot and scanner fallback.",
        "GROQ_TEXT_MODEL": "Optional override for the Groq chat model.",
        "API_BASE_URL": "Optional absolute API base for image URL generation.",
        "PORT": "Port used by the local app runner.",
    }
    for name in sorted(data["env_vars"]):
        pdf.bullet(f"{name}: {explanations.get(name, 'Referenced in code; inspect implementation for exact behavior.')}")
    pdf.body("Render service definition summary:")
    pdf.mono_block(summarize_text(data["top_files"].get("render.yaml", ""), "render.yaml not found"))


def add_dependencies(pdf: ManualPDF, data: dict[str, Any]):
    pdf.section_title("4. Tech Stack and Dependency Explanation")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for dep in data["requirements"]:
        grouped[dep["group"]].append(dep)
    descriptions = {
        "Core Framework": "HTTP API framework, request/response handling, and app wiring.",
        "Database": "ORM, migrations, and PostgreSQL connectivity.",
        "Auth": "Password hashing and JWT token support.",
        "Validation": "Schema-driven request validation.",
        "CORS": "Cross-origin browser access for the frontend.",
        "Rate Limiting": "Per-IP throttling for abuse control.",
        "AI (Groq - FREE)": "Model inference used by the AI planner and scanner fallback path.",
        "PDF Generation": "Creates exportable health reports and documentation PDFs.",
        "Scheduler (reminders)": "Background scheduling support.",
        "Environment": "Loads .env values into runtime config.",
        "HTTP": "Outgoing calls to remote AI and dataset endpoints.",
        "Development only": "Testing and development support.",
        "Deployment": "Production WSGI server."
    }
    for group, deps in grouped.items():
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, pdf_safe(group), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5.5, pdf_safe(descriptions.get(group, "Dependency group declared in requirements.txt.")))
        for dep in deps:
            version = f"=={dep['version']}" if dep["version"] else ""
            pdf.bullet(f"{dep['name']}{version}")
        pdf.ln(1)


def add_models(pdf: ManualPDF, data: dict[str, Any]):
    pdf.section_title("5. Data Model and Persistence")
    pdf.body("The backend persists application state in PostgreSQL through SQLAlchemy models.")
    for model_file in data["model_inventory"]:
        model_class = model_file["classes"][0] if model_file["classes"] else None
        title = model_class["name"] if model_class else model_file["relative_path"]
        summary = summarize_text(model_class["doc"] if model_class else model_file["doc"], "No class-level docstring found.")
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, pdf_safe(title), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5.5, pdf_safe(summary))
        if model_class and model_class["fields"]:
            pdf.bullet("Fields: " + ", ".join(model_class["fields"]))
        if model_class and model_class["methods"]:
            pdf.bullet("Methods: " + ", ".join(model_class["methods"]))
    pdf.body("Migration files currently tracked:")
    for path in sorted((ROOT_DIR / "migrations" / "versions").glob("*.py")):
        pdf.bullet(path.name)


def add_apis(pdf: ManualPDF, data: dict[str, Any]):
    pdf.section_title("6. API Surface")
    pdf.body("The endpoint list below is generated from route decorators inside the repository.")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for route in data["route_inventory"]:
        parts = route["path"].split("/", 3)
        domain = "/" + parts[2] if len(parts) > 2 else route["path"]
        grouped[domain].append(route)
    for domain in sorted(grouped):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, pdf_safe(f"Domain: {domain}"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9.5)
        for route in grouped[domain]:
            methods = ",".join(route["methods"])
            text = f"[{methods}] {route['path']} -> {route['function']}"
            if route["doc"]:
                text += f" | {summarize_text(route['doc'], '')}"
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, pdf_safe(text))
        pdf.ln(1)


def add_workflows(pdf: ManualPDF):
    pdf.section_title("7. Major Workflows and Data Flow")
    workflows = [
        ("Authentication and bootstrap", [
            "POST /api/register validates credentials, normalizes email, hashes password, and creates a User record.",
            "POST /api/login validates credentials, checks the bcrypt hash, and returns a JWT access token.",
            "Protected feature routes use jwt_required_custom, which validates the token and injects current_user into controllers.",
        ]),
        ("Health profile and recommendation refresh", [
            "POST /api/profile normalizes onboarding labels, calculates BMI/BMR/TDEE/daily calories, estimates body-fat percentage, and stores HealthProfile.",
            "The same save flow refreshes Recommendation content and clears active workout sessions so planning stays consistent after profile changes.",
        ]),
        ("Workout planning and execution", [
            "GET /api/workout/plan checks custom WorkoutPlan rows first; if absent, it generates a profile-driven plan from the exercise library.",
            "The planner combines goal-track templates, exercise scoring, goal-timeline estimation, and media-backed exercise records.",
            "Workout sessions can be started, progressed, completed, or reset, with ActivityLog entries written for completed or timed workouts.",
        ]),
        ("Food scanning and meal logging", [
            "POST /api/food/analyze-photo validates image size and MIME type, tries structured AI analysis, enriches with local food data, and falls back to keyword catalogs.",
            "When logging is requested, a meal ActivityLog is created and the uploaded image bytes are persisted alongside the record.",
            "GET /api/activity and GET /api/activity/<id>/image expose that history back to the frontend.",
        ]),
        ("Dashboard and progress aggregation", [
            "GET /api/dashboard summarizes current-day calories, water, streaks, weekly chart data, and motivational content.",
            "GET /api/progress builds chart-ready weekly or monthly trend data from ActivityLog plus profile state.",
            "GET /api/export/pdf converts profile and recent activity data into a PDF report.",
        ]),
        ("AI planner workflow", [
            "POST /api/ai/diet-chat detects a topic, loads profile and recent activity context, optionally pulls a workout plan, and builds a system prompt for Groq.",
            "If Groq is unavailable, the controller returns a rule-based fallback response that remains personalized from profile and activity context.",
        ]),
    ]
    for title, bullets in workflows:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, pdf_safe(title), new_x="LMARGIN", new_y="NEXT")
        for bullet in bullets:
            pdf.bullet(bullet)
        pdf.ln(1)
    pdf.mono_block(
        "Profile save -> HealthProfile updated -> BMI/BFP recalculated -> Recommendation refreshed ->\n"
        "Workout plan generated on demand -> Session execution -> ActivityLog updated -> Dashboard/Progress refreshed"
    )


def add_algorithms(pdf: ManualPDF):
    pdf.section_title("8. Key Algorithms, Technical Terms, and Concepts")
    concepts = [
        ("BMI", "Body Mass Index; implemented in utils/bmi_calculator.py as weight divided by squared height in meters."),
        ("BMR", "Basal Metabolic Rate; estimated with the Mifflin-St Jeor equation."),
        ("TDEE", "Total Daily Energy Expenditure; derived from BMR multiplied by an activity-level coefficient."),
        ("Daily calorie target", "Adjusted from TDEE according to fitness goal, with a minimum safety floor."),
        ("Estimated body fat", "Calculated with a Deurenberg-style heuristic in utils/body_fat.py."),
        ("Goal-period estimation", "Implemented in utils/goal_achievement_model.py using BMI/BFP reference rows plus heuristics to estimate weeks to target."),
        ("Exercise scoring", "Implemented in utils/workout_planner.py; exercises are ranked by category fit, muscle overlap, difficulty fit, and media availability."),
        ("Structured AI output", "Scanner utilities force Gemini or Groq to return strict JSON payloads for downstream nutrition processing."),
        ("Fallback catalog", "Keyword-to-food mappings used when vision is uncertain to keep the scanner usable in real-world conditions."),
        ("Persisted scan image", "Meal activity logs can store uploaded image bytes directly in the database and expose them through an authenticated endpoint."),
    ]
    for title, desc in concepts:
        pdf.bullet(f"{title}: {desc}")
    pdf.body("Algorithm highlights verified from repository code:")
    pdf.bullet("utils/goal_achievement_model.py computes target BMI/BFP values, safe weekly change rates, candidate distance against reference rows, and a weighted estimated-week result.")
    pdf.bullet("utils/workout_planner.py defines per-goal weekly tracks, maps user activity level to difficulty ceilings, scores exercise-library entries, prescribes sets/reps/duration/rest, and composes today/weekly plan payloads.")
    pdf.bullet("controllers/food_controller.py combines vision models, DB matching, fallback catalogs, macro scaling, scan recovery guidance, and goal-aware warnings.")
    pdf.bullet("controllers/ai_controller.py lazily loads workout context only for relevant topics to keep responses efficient.")


def add_file_breakdown(pdf: ManualPDF, data: dict[str, Any]):
    pdf.section_title("9. File-by-File Breakdown")
    for top_file in TOP_LEVEL_FILES:
        path = ROOT_DIR / top_file
        if not path.exists():
            continue
        if top_file.endswith(".py"):
            info = scan_python_file(path)
            desc = summarize_text(info["doc"], f"Top-level backend file: {top_file}")
        else:
            desc = {
                "README.md": "Getting-started guide, endpoint summary, and project notes. Some text is historical and no longer reflects newer backend upgrades.",
                "render.yaml": "Render deployment descriptor that defines build command, start command, plan, health check, and key environment variables.",
                "requirements.txt": "Pinned Python dependencies grouped by responsibility."
            }.get(top_file, f"Repository file: {top_file}")
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 7, pdf_safe(top_file), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5.5, pdf_safe(desc))
        if top_file.endswith(".py") and info["functions"]:
            pdf.bullet("Functions: " + ", ".join(item["name"] for item in info["functions"][:10]))
        pdf.ln(1)
    for folder in TARGET_DIRS:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, pdf_safe(f"Directory: {folder}"), new_x="LMARGIN", new_y="NEXT")
        for item in data["dirs"][folder]:
            summary = summarize_text(item["doc"], f"{folder} module.")
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 6, pdf_safe(item["relative_path"]), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, pdf_safe(summary))
            if item["classes"]:
                pdf.bullet("Classes: " + ", ".join(cls["name"] for cls in item["classes"]), size=9)
            if item["functions"]:
                pdf.bullet("Functions: " + ", ".join(func["name"] for func in item["functions"][:12]), size=9)
            if item["routes"]:
                pdf.bullet("Endpoints: " + ", ".join(route["path"] for route in item["routes"]), size=9)
        pdf.ln(1)


def add_limits(pdf: ManualPDF):
    pdf.section_title("10. Assumptions, Limitations, and Edge Cases")
    limits = [
        "README.md still contains older wording such as MySQL references and an older endpoint count, while the live code targets PostgreSQL/Neon and a richer feature set.",
        "Body-fat percentage is estimated heuristically; it is not a clinically measured value.",
        "Goal-period estimation is model-backed but lightweight. It uses reference datasets plus heuristics instead of a separately trained model artifact.",
        "Food scanning quality depends on upstream AI provider availability, image clarity, package readability, and fallback catalog coverage.",
        "Some AI integrations are environment-dependent. Runtime availability can vary by provider key, model support, quota, or geographic restrictions.",
        "The free exercise import script depends on either a local clone path or a remote GitHub dataset URL being reachable at import time.",
        "Scheduler configuration exists, but the repository does not define a persistent APScheduler job store within this codebase.",
        "The repository does not currently contain a broad automated test suite; correctness is driven mainly by runtime behavior and validation guards.",
    ]
    edge_cases = [
        "Missing health profile: profile, workout, and AI planner routes prompt profile creation.",
        "Invalid JWT: jwt_required_custom returns a standardized 401 response.",
        "Unclear food photo: scanner falls back from structured AI to coarse identification to DB/catalog matching and finally scan-recovery hints.",
        "No active workout session: session lookup returns 404 rather than silent success.",
        "Custom workout plan present: workout controller prefers custom plans over generated plans.",
        "Scan image retrieval without request context: ActivityLog.to_dict falls back to relative or configurable API URL generation.",
    ]
    pdf.body("Assumptions and limitations identified directly from code and repository contents:")
    for item in limits:
        pdf.bullet(item)
    pdf.body("Important edge cases handled in code:")
    for item in edge_cases:
        pdf.bullet(item)


def build_manual_pdf(data: dict[str, Any]) -> Path:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf = ManualPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    add_cover(pdf, data)
    add_project_overview(pdf)
    add_architecture(pdf)
    add_setup(pdf, data)
    add_dependencies(pdf, data)
    add_models(pdf, data)
    add_apis(pdf, data)
    add_workflows(pdf)
    add_algorithms(pdf)
    add_file_breakdown(pdf, data)
    add_limits(pdf)
    pdf.output(str(OUTPUT_PATH))
    return OUTPUT_PATH


def main():
    data = scan_repository()
    output = build_manual_pdf(data)
    print(output)


if __name__ == "__main__":
    main()
