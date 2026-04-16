"""Seed breakfast-only meal scan mock data for the demo account through today."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import base64
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from extensions import db
from models.activity_log import ActivityLog
from models.user import User


TARGET_EMAIL = "demo.fitlife.user@gmail.com"

# Tiny valid 1x1 PNG so breakfast scan history has persisted image-backed entries.
BREAKFAST_SCAN_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9r7d8AAAAASUVORK5CYII="
)


@dataclass(frozen=True)
class BreakfastScan:
    description: str
    calories: int


BREAKFAST_ROTATION = [
    BreakfastScan("Scanned Breakfast: Oats bowl with banana and almonds", 410),
    BreakfastScan("Scanned Breakfast: Idli with sambar and boiled egg", 430),
    BreakfastScan("Scanned Breakfast: Peanut butter toast with milk", 390),
    BreakfastScan("Scanned Breakfast: Vegetable poha with curd", 405),
]


def seed_for_user(user_email: str):
    user = User.query.filter_by(email=user_email).first()
    if not user:
        raise SystemExit(f"User not found: {user_email}")

    latest_breakfast = (
        ActivityLog.query.filter(
            ActivityLog.user_id == user.id,
            ActivityLog.log_type == "meal",
            ActivityLog.description.ilike("%breakfast%"),
        )
        .order_by(ActivityLog.log_date.desc(), ActivityLog.created_at.desc())
        .first()
    )

    start_date = (latest_breakfast.log_date + timedelta(days=1)) if latest_breakfast else (date.today() - timedelta(days=6))
    end_date = date.today()

    if start_date > end_date:
        print(f"No breakfast scan seeding needed for {user_email}; latest breakfast already covers {end_date}.")
        return

    inserted = 0
    current = start_date
    while current <= end_date:
        existing_breakfast = (
            ActivityLog.query.filter(
                ActivityLog.user_id == user.id,
                ActivityLog.log_date == current,
                ActivityLog.log_type == "meal",
                ActivityLog.description.ilike("%breakfast%"),
            )
            .order_by(ActivityLog.created_at.desc())
            .first()
        )

        if existing_breakfast and existing_breakfast.image_blob:
            current += timedelta(days=1)
            continue

        breakfast = BREAKFAST_ROTATION[current.toordinal() % len(BREAKFAST_ROTATION)]
        if existing_breakfast:
            existing_breakfast.description = breakfast.description
            existing_breakfast.calories_in = breakfast.calories
            existing_breakfast.image_blob = BREAKFAST_SCAN_PNG
            existing_breakfast.image_mime_type = "image/png"
            existing_breakfast.image_filename = f"breakfast-scan-{current.isoformat()}.png"
        else:
            db.session.add(
                ActivityLog(
                    user_id=user.id,
                    log_date=current,
                    log_type="meal",
                    description=breakfast.description,
                    calories_in=breakfast.calories,
                    image_blob=BREAKFAST_SCAN_PNG,
                    image_mime_type="image/png",
                    image_filename=f"breakfast-scan-{current.isoformat()}.png",
                )
            )
        inserted += 1
        current += timedelta(days=1)

    db.session.commit()
    print(f"Seeded/updated {inserted} breakfast scan logs for {user_email} through {end_date}.")


def main():
    app = create_app("production")
    with app.app_context():
        seed_for_user(TARGET_EMAIL)


if __name__ == "__main__":
    main()
