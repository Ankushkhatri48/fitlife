from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

from weight.models import WeightLog
from weight.forms import WeightLogForm
from nutrition.services import get_user_local_date

@login_required
def log_weight_view(request):
    user = request.user
    today = get_user_local_date(user)
    date_str = request.GET.get('date')
    
    target_date = today
    if date_str:
        try:
            target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
            
    # Check if a log already exists for this date
    log_entry = WeightLog.objects.filter(user=user, date=target_date).first()
    
    if request.method == 'POST':
        form = WeightLogForm(request.POST, instance=log_entry)
        if form.is_valid():
            new_log = form.save(commit=False)
            new_log.user = user
            new_log.date = form.cleaned_data.get('date') or target_date
            
            # Secure ownership check
            if log_entry and log_entry.user != user:
                return HttpResponseForbidden("You cannot edit this entry.")
                
            new_log.save()
            
            # Also update user's profile weight if this is the most recent log
            profile = user.profile
            latest_log = WeightLog.objects.filter(user=user).order_by('-date').first()
            if latest_log and latest_log.date == new_log.date:
                profile.weight = new_log.weight
                profile.weight_unit = new_log.unit
                profile.save()
                
            messages.success(request, f"Weight of {new_log.weight} {new_log.unit} logged successfully for {new_log.date}!")
            return redirect('weight:history')
        else:
            messages.error(request, "Failed to log weight. Please verify your inputs.")
    else:
        if log_entry:
            form = WeightLogForm(instance=log_entry)
        else:
            form = WeightLogForm(initial={'date': target_date, 'unit': user.profile.weight_unit})
            
    return render(request, 'weight/log_weight.html', {
        'form': form,
        'target_date': target_date,
        'is_edit': log_entry is not None
    })

@login_required
def delete_weight_view(request, pk):
    log_entry = get_object_or_404(WeightLog, pk=pk)
    if log_entry.user != request.user:
        return HttpResponseForbidden("You are not authorized to delete this log.")
        
    if request.method == 'POST':
        date_logged = log_entry.date
        log_entry.delete()
        
        # If the user deleted the latest weight, update profile weight to the next latest
        profile = request.user.profile
        latest_log = WeightLog.objects.filter(user=request.user).order_by('-date').first()
        if latest_log:
            profile.weight = latest_log.weight
            profile.weight_unit = latest_log.unit
            profile.save()
            
        messages.success(request, f"Deleted weight log for {date_logged}.")
        return redirect('weight:history')
    return render(request, 'weight/delete_confirm.html', {'entry': log_entry})

@login_required
def history_weight_view(request):
    logs_list = WeightLog.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(logs_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate starting, current, target, change
    first_log = WeightLog.objects.filter(user=request.user).order_by('date').first()
    latest_log = WeightLog.objects.filter(user=request.user).order_by('-date').first()
    
    start_weight = first_log.weight if first_log else request.user.profile.weight
    current_weight = latest_log.weight if latest_log else request.user.profile.weight
    unit = latest_log.unit if latest_log else request.user.profile.weight_unit
    
    weight_change = 0
    if start_weight and current_weight:
        weight_change = current_weight - start_weight
        
    context = {
        'page_obj': page_obj,
        'start_weight': start_weight,
        'current_weight': current_weight,
        'weight_unit': unit,
        'weight_change': weight_change,
        'goal': request.user.profile.goal,
    }
    return render(request, 'weight/history.html', context)
