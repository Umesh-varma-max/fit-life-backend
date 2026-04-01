"""
Goal mapping helpers for frontend goal labels and backend generation.
"""

GOAL_ALIAS_MAP = {
    'cut': 'weight_loss',
    'weight_loss': 'weight_loss',
    'bulk': 'muscle_gain',
    'muscle growth': 'muscle_gain',
    'muscle_growth': 'muscle_gain',
    'muscle gain': 'muscle_gain',
    'muscle_gain': 'muscle_gain',
    'fit': 'maintenance',
    'maintenance': 'maintenance'
}

GOAL_DISPLAY_LABELS = {
    'weight_loss': 'Cut',
    'muscle_gain': 'Muscle Growth',
    'maintenance': 'Fit'
}


def normalize_goal(goal: str, fallback: str = 'maintenance') -> str:
    """Map user-facing goal labels to canonical backend goals."""
    if not goal:
        return fallback
    cleaned = goal.strip().lower().replace('-', ' ').replace('_', ' ')
    return GOAL_ALIAS_MAP.get(cleaned, fallback)


def goal_label(goal: str) -> str:
    """Return the preferred UI display label for a canonical goal."""
    return GOAL_DISPLAY_LABELS.get(normalize_goal(goal), 'Fit')
