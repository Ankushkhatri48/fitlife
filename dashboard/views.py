from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
import json
from decimal import Decimal

from accounts.services import calculate_daily_targets, convert_to_metric
from nutrition.models import DailyNutritionEntry
from nutrition.services import get_user_local_date, calculate_streak_stats
from weight.models import WeightLog

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'dashboard/landing.html')

@login_required
def index_view(request):
    user = request.user
    profile = user.profile
    
    # Force onboarding if not completed
    if not profile.onboarded:
        return redirect('accounts:onboarding')
        
    today = get_user_local_date(user)
    
    # Calculate daily targets
    targets = calculate_daily_targets(profile)
    
    # Apply target overrides if set
    calorie_target = profile.daily_calorie_target_override or targets['calories']
    protein_target = profile.protein_target_override or targets['protein']
    carbs_target = profile.carbs_target_override or targets['carbs']
    fat_target = profile.fat_target_override or targets['fat']
    
    # Fetch today's entry
    entry = DailyNutritionEntry.objects.filter(user=user, date=today).first()
    
    # Current weight
    current_weight_log = WeightLog.objects.filter(user=user).order_by('-date').first()
    current_weight = current_weight_log.weight if current_weight_log else profile.weight
    weight_unit = current_weight_log.unit if current_weight_log else profile.weight_unit
    
    # Streak
    streak_stats = calculate_streak_stats(user)
    
    # Consumed values
    consumed = {
        'calories': entry.calories if entry else 0,
        'protein': entry.protein if entry else 0,
        'carbs': entry.carbohydrates if entry else 0,
        'fat': entry.fat if entry else 0,
        'caffeine': entry.caffeine if entry else 0,
        'sugar': entry.sugar if entry else 0,
    }
    
    remaining_calories = max(0, calorie_target - consumed['calories'])
    
    # Calorie target status
    calorie_diff = consumed['calories'] - calorie_target
    if abs(calorie_diff) <= 100:
        status = 'target'
        status_label = '🟢 Within calorie target'
    elif calorie_diff > 100:
        status = 'surplus'
        status_label = '🔴 Above calorie target'
    else:
        status = 'deficit'
        status_label = '🟡 Below target'
        
    # Fat equivalent calculation: 7700 kcal = 1 kg fat
    # estimated_fat_equivalent_kg = calorie_difference / 7700
    fat_eq = Decimal(str(calorie_diff)) / Decimal('7700')
    fat_eq = round(fat_eq, 2)
    
    context = {
        'today': today,
        'calorie_target': calorie_target,
        'protein_target': protein_target,
        'carbs_target': carbs_target,
        'fat_target': fat_target,
        'consumed': consumed,
        'remaining_calories': remaining_calories,
        'current_weight': current_weight,
        'weight_unit': weight_unit,
        'streak': streak_stats['current_streak'],
        'streak_stats': streak_stats,
        'goal': profile.goal,
        'status_label': status_label,
        'status': status,
        'fat_eq': fat_eq,
        'abs_fat_eq': abs(fat_eq),
        'entry': entry,
    }
    return render(request, 'dashboard/index.html', context)

@login_required
def progress_view(request):
    user = request.user
    profile = user.profile
    
    if not profile.onboarded:
        return redirect('accounts:onboarding')
        
    # Get timeframe (default 7 days)
    days_param = request.GET.get('days', '7')
    if days_param not in ['7', '30', '90']:
        days_param = '7'
    days_limit = int(days_param)
    
    today = get_user_local_date(user)
    start_date = today - timedelta(days=days_limit - 1)
    
    # Generate list of dates for the charts
    date_list = [start_date + timedelta(days=x) for x in range(days_limit)]
    date_strings = [d.strftime('%b %d') for d in date_list]
    
    # Fetch entries mapped by date
    entries = DailyNutritionEntry.objects.filter(
        user=user,
        date__range=[start_date, today]
    )
    entries_by_date = {e.date: e for e in entries}
    
    # Fetch weight logs mapped by date
    weight_logs = WeightLog.objects.filter(
        user=user,
        date__range=[start_date, today]
    )
    weight_by_date = {w.date: w for w in weight_logs}
    
    # Build chart datasets
    calorie_dataset = []
    protein_dataset = []
    carbs_dataset = []
    fat_dataset = []
    sugar_dataset = []
    caffeine_dataset = []
    weight_dataset = []
    
    # Fetch calorie target
    targets = calculate_daily_targets(profile)
    calorie_target = profile.daily_calorie_target_override or targets['calories']
    protein_target = profile.protein_target_override or targets['protein']
    
    # Last known weight helper
    last_known_weight = profile.weight
    first_weight_log = WeightLog.objects.filter(user=user).order_by('date').first()
    start_weight = first_weight_log.weight if first_weight_log else profile.weight
    
    for date in date_list:
        entry = entries_by_date.get(date)
        calorie_dataset.append(entry.calories if entry else 0)
        protein_dataset.append(entry.protein if entry else 0)
        carbs_dataset.append(entry.carbohydrates if entry else 0)
        fat_dataset.append(entry.fat if entry else 0)
        sugar_dataset.append(entry.sugar if entry else 0)
        caffeine_dataset.append(entry.caffeine if entry else 0)
        
        # Keep rolling weight or set 0 if not tracked
        w_log = weight_by_date.get(date)
        if w_log:
            last_known_weight = w_log.weight
            weight_dataset.append(float(w_log.weight))
        else:
            weight_dataset.append(float(last_known_weight) if last_known_weight else None)
            
    # Calculate starting, current, change
    current_weight_log = WeightLog.objects.filter(user=user).order_by('-date').first()
    current_weight = current_weight_log.weight if current_weight_log else profile.weight
    weight_unit = current_weight_log.unit if current_weight_log else profile.weight_unit
    
    weight_change = Decimal('0.0')
    if start_weight and current_weight:
        weight_change = current_weight - start_weight
        
    streak_stats = calculate_streak_stats(user)
    
    # Format data for templates
    context = {
        'days_limit': days_limit,
        'date_labels': json.dumps(date_strings),
        'calorie_data': json.dumps(calorie_dataset),
        'protein_data': json.dumps(protein_dataset),
        'carbs_data': json.dumps(carbs_dataset),
        'fat_data': json.dumps(fat_dataset),
        'sugar_data': json.dumps(sugar_dataset),
        'caffeine_data': json.dumps(caffeine_dataset),
        'weight_data': json.dumps(weight_dataset),
        'calorie_target': calorie_target,
        'protein_target': protein_target,
        'start_weight': start_weight,
        'current_weight': current_weight,
        'weight_change': weight_change,
        'weight_unit': weight_unit,
        'streak_stats': streak_stats,
    }
    
    return render(request, 'dashboard/progress.html', context)
