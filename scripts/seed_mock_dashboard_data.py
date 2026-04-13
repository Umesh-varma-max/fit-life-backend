"""Seed realistic dashboard/activity mock data for a demo user through today."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app
from extensions import db
from models.activity_log import ActivityLog
from models.user import User


TARGET_EMAIL = "demo.fitlife.user@gmail.com"


@dataclass(frozen=True)
class DailyMeal:
    label: str
    calories: int


MEAL_ROTATIONS = [
    [
        DailyMeal("Breakfast: Oats bowl with banana and almonds", 410),
        DailyMeal("Lunch: Grilled chicken salad with roti", 560),
        DailyMeal("Snack: Apple with roasted chana", 190),
        DailyMeal("Dinner: Fish curry with vegetables", 480),
    ],
    [
        DailyMeal("Breakfast: Idli with sambar and boiled egg", 430),
        DailyMeal("Lunch: Brown rice, dal, paneer, and salad", 610),
        DailyMeal("Snack: Greek yogurt with berries", 170),
        DailyMeal("Dinner: Stir-fried chicken with sauteed vegetables", 460),
    ],
    [
        DailyMeal("Breakfast: Peanut butter toast with milk", 390),
        DailyMeal("Lunch: Quinoa bowl with chicken and veggies", 540),
        DailyMeal("Snack: Mixed nuts and orange", 210),
        DailyMeal("Dinner: Grilled fish with soup and salad", 430),
    ],
]

WORKOUT_ROTATIONS = {
    0: ("Workout: Adaptive lower body circuit", 320, 42),   # Monday
    1: ("Workout: Conditioning core and cardio", 280, 36),  # Tuesday
    2: ("Workout: Upper body strength session", 300, 40),   # Wednesday
    3: None,                                                # Thursday recovery
    4: ("Workout: Full body fat-loss session", 340, 45),    # Friday
    5: ("Workout: Brisk walk and mobility", 220, 35),       # Saturday
    6: None,                                                # Sunday recovery
}

WATER_BY_WEEKDAY = {
    0: 2900,
    1: 3100,
    2: 2800,
    3: 2600,
    4: 3200,
    5: 3000,
    6: 2700,
}

SLEEP_BY_WEEKDAY = {
    0: Decimal("7.4"),
    1: Decimal("7.0"),
    2: Decimal("7.8"),
    3: Decimal("8.1"),
    4: Decimal("7.3"),
    5: Decimal("8.4"),
    6: Decimal("8.0"),
}


def seed_for_user(user_email: str):
    user = User.query.filter_by(email=user_email).first()
    if not user:
        raise SystemExit(f"User not found: {user_email}")

    latest = (
        ActivityLog.query.filter_by(user_id=user.id)
        .order_by(ActivityLog.log_date.desc(), ActivityLog.created_at.desc())
        .first()
    )
    start_date = (latest.log_date + timedelta(days=1)) if latest else (date.today() - timedelta(days=20))
    end_date = date.today()

    if start_date > end_date:
        print(f"No seeding needed for {user_email}; latest log already covers {end_date}.")
        return

    inserted = 0
    current = start_date
    while current <= end_date:
        weekday = current.weekday()
        meals = MEAL_ROTATIONS[(current.toordinal()) % len(MEAL_ROTATIONS)]

        for meal in meals:
            db.session.add(
                ActivityLog(
                    user_id=user.id,
                    log_date=current,
                    log_type="meal",
                    description=meal.label,
                    calories_in=meal.calories,
                )
            )
            inserted += 1

        db.session.add(
            ActivityLog(
                user_id=user.id,
                log_date=current,
                log_type="water",
                description="Daily water intake",
                water_ml=WATER_BY_WEEKDAY[weekday],
            )
        )
        inserted += 1

        db.session.add(
            ActivityLog(
                user_id=user.id,
                log_date=current,
                log_type="sleep",
                description="Night sleep",
                sleep_hours=SLEEP_BY_WEEKDAY[weekday],
            )
        )
        inserted += 1

        workout = WORKOUT_ROTATIONS.get(weekday)
        if workout:
            description, calories_out, duration_min = workout
            db.session.add(
                ActivityLog(
                    user_id=user.id,
                    log_date=current,
                    log_type="workout",
                    description=description,
                    calories_out=calories_out,
                    duration_min=duration_min,
                )
            )
            inserted += 1

        current += timedelta(days=1)

    db.session.commit()
    print(f"Inserted {inserted} logs for {user_email} from {start_date} to {end_date}.")


def main():
    app = create_app("production")
    with app.app_context():
        seed_for_user(TARGET_EMAIL)


if __name__ == "__main__":
    main()
