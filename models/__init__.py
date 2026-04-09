# models/__init__.py
# Import all models here so Flask-Migrate discovers them.

from models.user import User
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from models.recommendation import Recommendation
from models.food_item import FoodItem
from models.workout_plan import WorkoutPlan
from models.trainer import Trainer
from models.doctor import Doctor
from models.reminder import Reminder
from models.workout_session import WorkoutSession
from models.body_metric_reference import BodyMetricReference

__all__ = [
    'User', 'HealthProfile', 'ActivityLog', 'Recommendation',
    'FoodItem', 'WorkoutPlan', 'Trainer', 'Doctor', 'Reminder',
    'WorkoutSession', 'BodyMetricReference'
]
