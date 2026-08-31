from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseForbidden
from datetime import datetime, date
import calendar as pycalendar

from nutrition.models import DailyNutritionEntry
from nutrition.forms import DailyNutritionForm
from nutrition.services import get_user_local_date
from accounts.services import calculate_daily_targets

@login_required
def log_entry_view(request):
    user = request.user
    date_str = request.GET.get('date')
    
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            target_date = get_user_local_date(user)
    else:
        target_date = get_user_local_date(user)
        
    # Check if entry already exists
    entry = DailyNutritionEntry.objects.filter(user=user, date=target_date).first()
    
    # Get user's calorie target for live deficit preview
    targets = calculate_daily_targets(user.profile)
    calorie_target = user.profile.daily_calorie_target_override or targets['calories']
    
    if request.method == 'POST':
        form = DailyNutritionForm(request.POST, instance=entry)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.user = user
            # Force the date to be the one specified in the form or selected
            new_entry.date = form.cleaned_data.get('date') or target_date
            
            # Secure against changing someone else's log by manipulating post requests
            if entry and entry.user != user:
                return HttpResponseForbidden("You cannot edit this entry.")
                
            new_entry.save()
            messages.success(request, f"Nutrition log saved successfully for {new_entry.date}!")
            return redirect('dashboard:index')
        else:
            messages.error(request, "Failed to save nutrition log. Please verify your input.")
    else:
        if entry:
            form = DailyNutritionForm(instance=entry)
        else:
            form = DailyNutritionForm(initial={'date': target_date})
            
    return render(request, 'nutrition/log_entry.html', {
        'form': form,
        'target_date': target_date,
        'calorie_target': calorie_target,
        'is_edit': entry is not None
    })

@login_required
def delete_entry_view(request, pk):
    entry = get_object_or_404(DailyNutritionEntry, pk=pk)
    if entry.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this record.")
        
    if request.method == 'POST':
        date_logged = entry.date
        entry.delete()
        messages.success(request, f"Deleted nutrition log for {date_logged}.")
        return redirect('nutrition:history')
    return render(request, 'nutrition/delete_confirm.html', {'entry': entry})

@login_required
def history_view(request):
    user = request.user
    targets = calculate_daily_targets(user.profile)
    user_target = user.profile.daily_calorie_target_override or targets['calories']

    entries_list = DailyNutritionEntry.objects.filter(user=user).order_by('-date')
    paginator = Paginator(entries_list, 10) # 10 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate daily deficit & fat metrics for each day in history
    for entry in page_obj:
        effective_burned = entry.calories_burned if entry.calories_burned > 0 else user_target
        net = entry.calories - effective_burned
        fat_g = abs(net) / 7.7
        entry.net_deficit = net
        entry.abs_net = abs(net)
        entry.is_deficit = net < 0
        entry.is_surplus = net > 0
        entry.effective_burned = effective_burned
        entry.fat_str = f"{round(fat_g/1000, 2)} kg" if fat_g >= 1000 else f"{int(round(fat_g))}g"

    return render(request, 'nutrition/history.html', {
        'page_obj': page_obj,
        'user_target': user_target
    })

@login_required
def calendar_view(request):
    user = request.user
    today = get_user_local_date(user)
    
    # Get requested year and month
    year_param = request.GET.get('year')
    month_param = request.GET.get('month')
    
    try:
        year = int(year_param) if year_param else today.year
        month = int(month_param) if month_param else today.month
        # Guard against invalid months
        if month < 1 or month > 12:
            raise ValueError
    except ValueError:
        year, month = today.year, today.month
        
    # Calculate next/previous months
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
        
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
        
    # Get all entries for this user in this month
    entries = DailyNutritionEntry.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    )
    # Put them in a set for O(1) lookups
    logged_dates = {e.date for e in entries}
    
    # Generate calendar matrix
    cal = pycalendar.Calendar(firstweekday=pycalendar.SUNDAY)
    month_days = cal.monthdays2calendar(year, month)
    
    month_days_data = []
    for week in month_days:
        week_data = []
        for day, wday in week:
            if day == 0:
                week_data.append({'day': 0})
            else:
                day_date = date(year, month, day)
                week_data.append({
                    'day': day,
                    'date_str': f"{year}-{month:02d}-{day:02d}",
                    'is_logged': day_date in logged_dates,
                    'is_today': day_date == today
                })
        month_days_data.append(week_data)
        
    month_name = pycalendar.month_name[month]
    
    context = {
        'year': year,
        'month': month,
        'month_name': month_name,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'month_days': month_days_data,
        'today': today,
    }
    return render(request, 'nutrition/calendar.html', context)

@login_required
def calorie_calculator_view(request):
    user = request.user
    today = get_user_local_date(user)
    
    if request.method == 'POST':
        # User wants to add the calculated calories to their log
        calories = int(request.POST.get('total_calories', 0))
        protein = int(request.POST.get('total_protein', 0))
        carbs = int(request.POST.get('total_carbs', 0))
        fat = int(request.POST.get('total_fat', 0))
        
        # Notes formatting
        notes_input = request.POST.get('notes', '').strip()
        
        # Look up or create log for today
        entry, created = DailyNutritionEntry.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'calories': calories,
                'protein': protein,
                'carbohydrates': carbs,
                'fat': fat,
                'notes': f"Added via Calorie Calculator:\n{notes_input}" if notes_input else "Added via Calorie Calculator"
            }
        )
        
        if not created:
            entry.calories += calories
            entry.protein += protein
            entry.carbohydrates += carbs
            entry.fat += fat
            if notes_input:
                entry.notes = f"{entry.notes}\n\nAdded via Calorie Calculator:\n{notes_input}" if entry.notes else f"Added via Calorie Calculator:\n{notes_input}"
            entry.save()
            
        messages.success(request, f"Added {calories} kcal and {protein}g protein to today's log!")
        return redirect('dashboard:index')
        
    return render(request, 'nutrition/calorie_calculator.html', {'today': today})

@login_required
def caffeine_calculator_view(request):
    user = request.user
    today = get_user_local_date(user)
    
    if request.method == 'POST':
        caffeine_mg = int(request.POST.get('total_caffeine_mg', 0))
        serving_type = request.POST.get('serving_type')
        servings = float(request.POST.get('servings', 1))
        
        custom_brand = request.POST.get('custom_brand', serving_type).strip() or serving_type
        weight = request.POST.get('weight', '').strip()
        weight_unit = request.POST.get('weight_unit', '').strip()
        
        weight_str = f" ({weight} {weight_unit})" if weight else ""
        caffeine_note = f"Caffeine: {servings} serving(s) of {custom_brand}{weight_str} ({caffeine_mg} mg total)"
        
        if caffeine_mg > 0:
            entry, created = DailyNutritionEntry.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'calories': 0,
                    'protein': 0,
                    'caffeine': caffeine_mg,
                    'notes': caffeine_note
                }
            )
            
            if not created:
                entry.caffeine += caffeine_mg
                entry.notes = f"{entry.notes}\n{caffeine_note}" if entry.notes else caffeine_note
                entry.save()
                
            messages.success(request, f"Recorded {caffeine_mg} mg of caffeine to today's log!")
        else:
            messages.error(request, "Invalid caffeine amount. Please enter a valid record.")
        return redirect('dashboard:index')
        
    return render(request, 'nutrition/caffeine_calculator.html')

@login_required
def sugar_calculator_view(request):
    user = request.user
    today = get_user_local_date(user)
    
    if request.method == 'POST':
        sugar_g = int(round(float(request.POST.get('total_sugar_g', 0))))
        source = request.POST.get('sugar_source', 'Custom')
        quantity = request.POST.get('quantity', '1')
        unit = request.POST.get('unit', 'grams')
        
        sugar_calories = sugar_g * 4
        sugar_note = f"Sugar: {quantity} {unit} of {source} ({sugar_g}g / ~{sugar_calories} kcal)"
        
        if sugar_g > 0:
            entry, created = DailyNutritionEntry.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'calories': sugar_calories,
                    'protein': 0,
                    'sugar': sugar_g,
                    'notes': sugar_note
                }
            )
            
            if not created:
                entry.sugar += sugar_g
                entry.calories += sugar_calories
                entry.notes = f"{entry.notes}\n{sugar_note}" if entry.notes else sugar_note
                entry.save()
                
            messages.success(request, f"Recorded {sugar_g}g of sugar (~{sugar_calories} kcal) to today's log!")
        else:
            messages.error(request, "Invalid sugar amount. Please enter a valid record.")
        return redirect('dashboard:index')
        
    return render(request, 'nutrition/sugar_calculator.html')
