from datetime import timedelta
import pytz
from django.utils import timezone
from nutrition.models import DailyNutritionEntry

def get_user_local_date(user):
    """
    Returns today's date adjusted to the user's timezone.
    """
    tz_name = user.profile.timezone
    try:
        user_tz = pytz.timezone(tz_name)
    except Exception:
        user_tz = pytz.UTC
    return timezone.now().astimezone(user_tz).date()

def calculate_streak_stats(user):
    """
    Calculates current streak, longest streak, days tracked, and missed days.
    A day is counted as complete when both calories > 0 and protein > 0.
    """
    today = get_user_local_date(user)
    
    # Get all entries for this user where calories > 0 and protein > 0
    completed_entries = DailyNutritionEntry.objects.filter(
        user=user,
        calories__gt=0,
        protein__gt=0
    ).order_by('-date')
    
    completed_dates = sorted(list(set(entry.date for entry in completed_entries)), reverse=True)
    
    days_tracked = len(completed_dates)
    
    if not completed_dates:
        # Check missed days from user creation
        reg_date = user.date_joined.date()
        total_days = (today - reg_date).days
        return {
            'current_streak': 0,
            'longest_streak': 0,
            'days_tracked': 0,
            'missed_days': max(0, total_days)
        }
        
    # Current Streak Calculation
    current_streak = 0
    if completed_dates[0] == today:
        current_streak = 1
        check_date = today - timedelta(days=1)
        for date in completed_dates[1:]:
            if date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
    elif completed_dates[0] == today - timedelta(days=1):
        current_streak = 1
        check_date = today - timedelta(days=2)
        for date in completed_dates[1:]:
            if date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
    else:
        current_streak = 0
        
    # Longest Streak Calculation
    longest_streak = 0
    if completed_dates:
        # Sort in ascending order to find streaks sequentially
        asc_dates = sorted(completed_dates)
        temp_streak = 1
        longest_streak = 1
        for i in range(1, len(asc_dates)):
            if asc_dates[i] == asc_dates[i-1] + timedelta(days=1):
                temp_streak += 1
            else:
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak
    
    # Calculate Missed Days:
    # Days between registration (or first entry if earlier) and today, minus completed tracking days.
    reg_date = user.date_joined.date()
    start_date = min(reg_date, completed_dates[-1]) if completed_dates else reg_date
    total_days_since_start = (today - start_date).days + 1 # inclusive
    
    # Find active logged entries
    logged_count = len(completed_dates)
    missed_days = max(0, total_days_since_start - logged_count)
    
    return {
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'days_tracked': days_tracked,
        'missed_days': missed_days
    }
