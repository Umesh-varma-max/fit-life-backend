"""
Goal-based workout templates with posture guidance and calorie estimates.
"""

DAY_ORDER = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

GOAL_TO_WORKOUT_KEY = {
    'weight_loss': 'cardio',
    'muscle_gain': 'strength',
    'maintenance': 'mixed'
}

BASE_WORKOUT_TEMPLATES = {
    'cardio': {
        'Mon': [
            {'name': 'Brisk Walk / Jog', 'duration_min': 30, 'sets': 0, 'reps': 0},
            {'name': 'Core Crunches', 'duration_min': 0, 'sets': 3, 'reps': 20}
        ],
        'Tue': [
            {'name': 'Cycling / Stationary Bike', 'duration_min': 30, 'sets': 0, 'reps': 0}
        ],
        'Wed': [
            {'name': 'Rest / Light Yoga', 'duration_min': 20, 'sets': 0, 'reps': 0}
        ],
        'Thu': [
            {'name': 'HIIT Circuit', 'duration_min': 25, 'sets': 0, 'reps': 0},
            {'name': 'Jumping Jacks', 'duration_min': 0, 'sets': 3, 'reps': 30}
        ],
        'Fri': [
            {'name': 'Swimming / Skipping', 'duration_min': 30, 'sets': 0, 'reps': 0}
        ],
        'Sat': [
            {'name': 'Long Walk / Hike', 'duration_min': 45, 'sets': 0, 'reps': 0}
        ],
        'Sun': [
            {'name': 'Rest & Recovery', 'duration_min': 0, 'sets': 0, 'reps': 0}
        ]
    },
    'strength': {
        'Mon': [
            {'name': 'Bench Press', 'duration_min': 0, 'sets': 4, 'reps': 10},
            {'name': 'Dumbbell Curl', 'duration_min': 0, 'sets': 3, 'reps': 12},
            {'name': 'Push-ups', 'duration_min': 0, 'sets': 3, 'reps': 15}
        ],
        'Tue': [
            {'name': 'Squats', 'duration_min': 0, 'sets': 4, 'reps': 12},
            {'name': 'Lunges', 'duration_min': 0, 'sets': 3, 'reps': 10},
            {'name': 'Leg Press', 'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Wed': [
            {'name': 'Rest / Stretching', 'duration_min': 20, 'sets': 0, 'reps': 0}
        ],
        'Thu': [
            {'name': 'Deadlifts', 'duration_min': 0, 'sets': 4, 'reps': 8},
            {'name': 'Pull-ups', 'duration_min': 0, 'sets': 3, 'reps': 8},
            {'name': 'Barbell Rows', 'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Fri': [
            {'name': 'Shoulder Press', 'duration_min': 0, 'sets': 4, 'reps': 10},
            {'name': 'Lateral Raise', 'duration_min': 0, 'sets': 3, 'reps': 15},
            {'name': 'Tricep Dips', 'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Sat': [
            {'name': 'Full Body Circuit', 'duration_min': 30, 'sets': 0, 'reps': 0}
        ],
        'Sun': [
            {'name': 'Rest & Recovery', 'duration_min': 0, 'sets': 0, 'reps': 0}
        ]
    },
    'mixed': {
        'Mon': [
            {'name': '30min Cardio + Core', 'duration_min': 40, 'sets': 0, 'reps': 0}
        ],
        'Tue': [
            {'name': 'Upper Body Strength', 'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Wed': [
            {'name': 'Rest or Yoga', 'duration_min': 20, 'sets': 0, 'reps': 0}
        ],
        'Thu': [
            {'name': 'HIIT 25min', 'duration_min': 25, 'sets': 0, 'reps': 0}
        ],
        'Fri': [
            {'name': 'Lower Body Strength', 'duration_min': 0, 'sets': 3, 'reps': 12}
        ],
        'Sat': [
            {'name': '45min Steady Cardio', 'duration_min': 45, 'sets': 0, 'reps': 0}
        ],
        'Sun': [
            {'name': 'Rest', 'duration_min': 0, 'sets': 0, 'reps': 0}
        ]
    }
}

POSTURE_LIBRARY = {
    'Brisk Walk / Jog': {
        'posture': 'Upright walking posture',
        'posture_cues': [
            'Keep shoulders relaxed and chest open.',
            'Land softly and keep your core lightly engaged.'
        ],
        'calories_per_min': 6.0
    },
    'Core Crunches': {
        'posture': 'Neutral-neck crunch posture',
        'posture_cues': [
            'Keep lower back gently pressed into the mat.',
            'Lift with your core, not by pulling the neck.'
        ],
        'calories_per_rep': 0.35
    },
    'Cycling / Stationary Bike': {
        'posture': 'Bike saddle posture',
        'posture_cues': [
            'Keep knees tracking straight forward.',
            'Hinge slightly at the hips without rounding the back.'
        ],
        'calories_per_min': 7.0
    },
    'Rest / Light Yoga': {
        'posture': 'Gentle recovery flow',
        'posture_cues': [
            'Move slowly through each stretch.',
            'Breathe evenly and avoid forcing range of motion.'
        ],
        'calories_per_min': 2.5
    },
    'HIIT Circuit': {
        'posture': 'Athletic ready stance',
        'posture_cues': [
            'Keep knees soft and core braced between moves.',
            'Land softly and maintain stable breathing.'
        ],
        'calories_per_min': 10.0
    },
    'Jumping Jacks': {
        'posture': 'Tall jumping-jack posture',
        'posture_cues': [
            'Land with knees slightly bent.',
            'Keep arms controlled instead of swinging wildly.'
        ],
        'calories_per_rep': 0.25
    },
    'Swimming / Skipping': {
        'posture': 'Rhythmic cardio posture',
        'posture_cues': [
            'Maintain smooth breathing rhythm.',
            'Keep movements light and repeatable.'
        ],
        'calories_per_min': 9.0
    },
    'Long Walk / Hike': {
        'posture': 'Tall hiking posture',
        'posture_cues': [
            'Look forward instead of down at your feet.',
            'Use natural arm swing to maintain balance.'
        ],
        'calories_per_min': 5.5
    },
    'Rest & Recovery': {
        'posture': 'Recovery posture',
        'posture_cues': [
            'Prioritize gentle mobility and easy breathing.',
            'Treat the day as active recovery, not inactivity guilt.'
        ],
        'calories_per_min': 1.5
    },
    'Bench Press': {
        'posture': 'Bench press setup',
        'posture_cues': [
            'Keep feet planted and shoulder blades pinned back.',
            'Lower the bar with elbows under control.'
        ],
        'calories_per_rep': 0.5
    },
    'Dumbbell Curl': {
        'posture': 'Elbows-tucked curl posture',
        'posture_cues': [
            'Keep elbows close to your torso.',
            'Avoid swinging or leaning back.'
        ],
        'calories_per_rep': 0.3
    },
    'Push-ups': {
        'posture': 'Straight-line plank posture',
        'posture_cues': [
            'Keep hips in line with shoulders and heels.',
            'Lower chest and hips together.'
        ],
        'calories_per_rep': 0.45
    },
    'Squats': {
        'posture': 'Hip-back squat posture',
        'posture_cues': [
            'Sit back into the hips and keep chest proud.',
            'Track knees over toes.'
        ],
        'calories_per_rep': 0.5
    },
    'Lunges': {
        'posture': 'Split-stance lunge posture',
        'posture_cues': [
            'Keep the front knee stacked over the ankle.',
            'Lower straight down instead of drifting forward.'
        ],
        'calories_per_rep': 0.45
    },
    'Leg Press': {
        'posture': 'Supported leg-press posture',
        'posture_cues': [
            'Keep lower back supported by the seat.',
            'Avoid locking out the knees at the top.'
        ],
        'calories_per_rep': 0.45
    },
    'Rest / Stretching': {
        'posture': 'Stretch-and-breathe posture',
        'posture_cues': [
            'Move gently into each stretch.',
            'Keep breathing slow and relaxed.'
        ],
        'calories_per_min': 2.0
    },
    'Deadlifts': {
        'posture': 'Hip-hinge deadlift posture',
        'posture_cues': [
            'Brace your core and keep the bar close to your legs.',
            'Drive through the floor and avoid rounding the back.'
        ],
        'calories_per_rep': 0.7
    },
    'Pull-ups': {
        'posture': 'Hollow-body pull-up posture',
        'posture_cues': [
            'Start from a stable hang with shoulders engaged.',
            'Pull chest toward the bar without swinging.'
        ],
        'calories_per_rep': 0.8
    },
    'Barbell Rows': {
        'posture': 'Flat-back rowing posture',
        'posture_cues': [
            'Keep torso braced and spine neutral.',
            'Row elbows back without shrugging shoulders.'
        ],
        'calories_per_rep': 0.55
    },
    'Shoulder Press': {
        'posture': 'Stacked overhead press posture',
        'posture_cues': [
            'Keep ribs down and glutes lightly engaged.',
            'Press overhead in a straight path.'
        ],
        'calories_per_rep': 0.45
    },
    'Lateral Raise': {
        'posture': 'Soft-elbow raise posture',
        'posture_cues': [
            'Lift with control and avoid shrugging.',
            'Stop around shoulder height.'
        ],
        'calories_per_rep': 0.25
    },
    'Tricep Dips': {
        'posture': 'Shoulders-down dip posture',
        'posture_cues': [
            'Keep shoulders away from ears.',
            'Lower only as far as your shoulders stay comfortable.'
        ],
        'calories_per_rep': 0.35
    },
    'Full Body Circuit': {
        'posture': 'Athletic circuit posture',
        'posture_cues': [
            'Stay light on your feet between moves.',
            'Maintain posture quality even as fatigue rises.'
        ],
        'calories_per_min': 8.0
    },
    '30min Cardio + Core': {
        'posture': 'Cardio-core combo posture',
        'posture_cues': [
            'Keep the ribcage stacked over the hips.',
            'Transition smoothly between cardio and core work.'
        ],
        'calories_per_min': 7.0
    },
    'Upper Body Strength': {
        'posture': 'Balanced upper-body lifting posture',
        'posture_cues': [
            'Keep shoulders packed and wrists neutral.',
            'Control each rep rather than rushing.'
        ],
        'calories_per_rep': 0.45
    },
    'Rest or Yoga': {
        'posture': 'Easy yoga posture',
        'posture_cues': [
            'Use slow transitions and easy breathing.',
            'Treat flexibility as recovery work, not strain.'
        ],
        'calories_per_min': 2.5
    },
    'HIIT 25min': {
        'posture': 'Explosive but controlled posture',
        'posture_cues': [
            'Keep landings quiet and controlled.',
            'Reset posture before each high-power move.'
        ],
        'calories_per_min': 10.0
    },
    'Lower Body Strength': {
        'posture': 'Stable lower-body lifting posture',
        'posture_cues': [
            'Brace your core and keep knees tracking cleanly.',
            'Use full range only where posture stays stable.'
        ],
        'calories_per_rep': 0.5
    },
    '45min Steady Cardio': {
        'posture': 'Steady-state cardio posture',
        'posture_cues': [
            'Maintain a pace where breathing stays controlled.',
            'Relax shoulders and stay tall throughout.'
        ],
        'calories_per_min': 6.5
    },
    'Rest': {
        'posture': 'Complete rest posture',
        'posture_cues': [
            'Use light stretching if you feel stiff.',
            'Allow recovery to support the next training day.'
        ],
        'calories_per_min': 1.0
    }
}

DEFAULT_POSTURE = {
    'posture': 'Controlled neutral posture',
    'posture_cues': [
        'Keep your core lightly braced.',
        'Move with control and full attention to form.'
    ],
    'calories_per_min': 5.0,
    'calories_per_rep': 0.35
}


def goal_to_workout_key(goal: str) -> str:
    """Map a fitness goal to a workout template key."""
    return GOAL_TO_WORKOUT_KEY.get(goal, 'mixed')


def _estimate_duration_min(exercise: dict) -> int:
    duration_min = int(exercise.get('duration_min') or 0)
    if duration_min > 0:
        return duration_min

    sets = int(exercise.get('sets') or 0)
    reps = int(exercise.get('reps') or 0)
    if sets and reps:
        return max(10, round((sets * reps) / 6))
    if sets:
        return max(8, sets * 3)
    return 0


def _estimate_calories_burn(exercise: dict, posture_meta: dict) -> int:
    duration_min = int(exercise.get('duration_min') or 0)
    if duration_min > 0:
        return int(round(duration_min * posture_meta.get('calories_per_min', 5.0)))

    sets = int(exercise.get('sets') or 0)
    reps = int(exercise.get('reps') or 0)
    if sets and reps:
        return int(round(sets * reps * posture_meta.get('calories_per_rep', 0.35)))
    if sets:
        return int(round(sets * posture_meta.get('calories_per_set', 6)))
    return 0


def enrich_exercise(exercise: dict) -> dict:
    """Add posture guidance and calorie-burn estimates to an exercise."""
    name = exercise.get('name', 'Exercise')
    posture_meta = POSTURE_LIBRARY.get(name, DEFAULT_POSTURE)
    estimated_duration = _estimate_duration_min(exercise)
    estimated_burn = _estimate_calories_burn(exercise, posture_meta)
    duration_min = int(exercise.get('duration_min') or 0)
    duration_seconds = int(exercise.get('duration_seconds') or (duration_min * 60 if duration_min else estimated_duration * 60))
    rest_seconds = int(exercise.get('rest_seconds') or (45 if exercise.get('sets') else 30))

    return {
        'name': name,
        'duration_min': duration_min,
        'duration_seconds': duration_seconds,
        'rest_seconds': rest_seconds,
        'sets': int(exercise.get('sets') or 0),
        'reps': int(exercise.get('reps') or 0),
        'muscle_group': exercise.get('muscle_group') or name.split()[-1].lower(),
        'description': exercise.get('description') or posture_meta['posture'],
        'instructions': exercise.get('instructions') or posture_meta['posture_cues'],
        'exercise_tips': exercise.get('exercise_tips') or posture_meta['posture_cues'],
        'gif_url': exercise.get('gif_url'),
        'image_url': exercise.get('image_url'),
        'video_url': exercise.get('video_url'),
        'demo_media_url': exercise.get('demo_media_url') or exercise.get('gif_url') or exercise.get('image_url') or exercise.get('video_url'),
        'posture': posture_meta['posture'],
        'posture_cues': posture_meta['posture_cues'],
        'estimated_duration_min': estimated_duration,
        'estimated_calories_burn': estimated_burn
    }


def build_workout_day(day: str, exercises: list, plan_name: str = None) -> dict:
    """Build a display-friendly workout day with totals."""
    enriched_exercises = [enrich_exercise(exercise) for exercise in (exercises or [])]
    total_duration = sum(exercise['estimated_duration_min'] for exercise in enriched_exercises)
    total_burn = sum(exercise['estimated_calories_burn'] for exercise in enriched_exercises)

    return {
        'day': day,
        'plan_name': plan_name or f'{day} Workout',
        'total_duration_min': total_duration,
        'total_estimated_calories_burn': total_burn,
        'exercises': enriched_exercises
    }


def build_goal_based_workout_plan(goal: str) -> dict:
    """Return a weekly workout plan tailored to the user's goal."""
    template_key = goal if goal in BASE_WORKOUT_TEMPLATES else goal_to_workout_key(goal)
    template = BASE_WORKOUT_TEMPLATES[template_key]
    days = [
        build_workout_day(day, template.get(day, []), f'{day} {template_key.title()} Plan')
        for day in DAY_ORDER
    ]

    return {
        'goal': goal,
        'template_key': template_key,
        'total_days': len(days),
        'active_days': sum(1 for day in days if day['total_duration_min'] > 0),
        'total_duration_min': sum(day['total_duration_min'] for day in days),
        'total_estimated_calories_burn': sum(day['total_estimated_calories_burn'] for day in days),
        'days': days
    }
