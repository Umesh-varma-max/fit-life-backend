# utils/quote_generator.py
"""
Daily motivational quotes.
Rotates based on day-of-year so each day gets a consistent quote.
"""

from datetime import date

QUOTES = [
    "Every rep brings you closer to your goal! 💪",
    "Your body can stand almost anything. It's your mind you have to convince.",
    "The only bad workout is the one that didn't happen.",
    "Take care of your body. It's the only place you have to live.",
    "Strength does not come from the body. It comes from the will.",
    "Don't stop when you're tired. Stop when you're done.",
    "Sweat is just fat crying. Keep going!",
    "The pain you feel today will be the strength you feel tomorrow.",
    "Fitness is not about being better than someone else. It's about being better than you used to be.",
    "A one-hour workout is 4% of your day. No excuses.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never came from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn't just find you. You have to go out and get it.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Do something today that your future self will thank you for.",
    "Little things make big days. Track every meal, crush every workout.",
    "It's going to be hard, but hard does not mean impossible.",
    "Don't wait for opportunity. Create it.",
    "You are one workout away from a good mood.",
    "Eat clean, train dirty.",
    "The best project you'll ever work on is you.",
    "Strive for progress, not perfection.",
    "Your health is an investment, not an expense.",
    "Believe in yourself and all that you are.",
    "The body achieves what the mind believes.",
    "Small daily improvements are the key to staggering long-term results.",
    "Discipline is choosing between what you want now and what you want most.",
    "Make yourself a priority. You deserve it.",
    "Today's pain is tomorrow's power.",
]


def get_daily_quote() -> str:
    """Returns a motivational quote that rotates daily."""
    day_of_year = date.today().timetuple().tm_yday
    index = day_of_year % len(QUOTES)
    return QUOTES[index]
