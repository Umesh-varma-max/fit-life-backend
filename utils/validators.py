# utils/validators.py
"""
Custom validation helpers for data sanitization and parsing.
"""

from datetime import datetime, date, time
import re


def normalize_email(email: str) -> str:
    """Lowercase and strip whitespace from email."""
    return email.strip().lower()


def parse_time_string(time_str: str) -> time:
    """
    Parse HH:MM or HH:MM:SS string to a time object.
    Raises ValueError if format is invalid.
    """
    time_str = time_str.strip()

    # Try HH:MM format
    if re.match(r'^\d{1,2}:\d{2}$', time_str):
        parts = time_str.split(':')
        return time(int(parts[0]), int(parts[1]))

    # Try HH:MM:SS format
    if re.match(r'^\d{1,2}:\d{2}:\d{2}$', time_str):
        parts = time_str.split(':')
        return time(int(parts[0]), int(parts[1]), int(parts[2]))

    raise ValueError(f"Invalid time format: {time_str}. Use HH:MM or HH:MM:SS.")


def parse_date_string(date_str: str) -> date:
    """
    Parse YYYY-MM-DD string to a date object.
    Returns today's date if None or empty.
    """
    if not date_str:
        return date.today()
    return datetime.strptime(date_str.strip(), '%Y-%m-%d').date()


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Strip whitespace and truncate to max length."""
    if not value:
        return ''
    return value.strip()[:max_length]
