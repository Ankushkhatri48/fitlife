import os
import urllib.parse
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser, UserProfile
from accounts.forms import RegistrationForm, UserProfileForm
from weight.models import WeightLog
from decimal import Decimal

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Fitness Tracker.")
            return redirect('accounts:onboarding')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        email_or_username = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try custom backend (email login fallback or authenticating directly)
        user = None
        if '@' in email_or_username:
            # Look up email
            try:
                user_obj = CustomUser.objects.get(email=email_or_username)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        else:
            user = authenticate(request, username=email_or_username, password=password)
            
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            if not user.profile.onboarded:
                return redirect('accounts:onboarding')
            return redirect('dashboard:index')
        else:
            messages.error(request, "Invalid login credentials. Please try again.")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('dashboard:landing')

@login_required
def onboarding_view(request):
    profile = request.user.profile
    if profile.onboarded:
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile_instance = form.save(commit=False)
            
            # Retrieve height_feet / height_inches custom form fields
            height_unit = form.cleaned_data.get('height_unit')
            if height_unit == 'ft_in':
                profile_instance.height_feet = form.cleaned_data.get('height_feet')
                profile_instance.height_inches = form.cleaned_data.get('height_inches')
                # Calculate cm equivalent for internal calculations
                feet = Decimal(str(profile_instance.height_feet or 0))
                inches = Decimal(str(profile_instance.height_inches or 0))
                total_inches = (feet * Decimal('12')) + inches
                profile_instance.height = total_inches * Decimal('2.54')
            else:
                profile_instance.height_feet = None
                profile_instance.height_inches = None
                
            profile_instance.onboarded = True
            profile_instance.save()
            
            # Log starting weight automatically
            if profile_instance.weight:
                WeightLog.objects.update_or_create(
                    user=request.user,
                    date=timezone.localdate(),
                    defaults={
                        'weight': profile_instance.weight,
                        'unit': profile_instance.weight_unit
                    }
                )
                
            messages.success(request, "Your profile details have been saved successfully!")
            return redirect('dashboard:index')
        else:
            messages.error(request, "Failed to save profile. Please fix the highlighted errors.")
    else:
        form = UserProfileForm(instance=profile)
        
    return render(request, 'accounts/onboarding.html', {'form': form})

@login_required
def profile_settings_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile_instance = form.save(commit=False)
            height_unit = form.cleaned_data.get('height_unit')
            if height_unit == 'ft_in':
                profile_instance.height_feet = form.cleaned_data.get('height_feet')
                profile_instance.height_inches = form.cleaned_data.get('height_inches')
                feet = Decimal(str(profile_instance.height_feet or 0))
                inches = Decimal(str(profile_instance.height_inches or 0))
                total_inches = (feet * Decimal('12')) + inches
                profile_instance.height = total_inches * Decimal('2.54')
            else:
                profile_instance.height_feet = None
                profile_instance.height_inches = None
            profile_instance.save()
            
            messages.success(request, "Settings updated successfully!")
            return redirect('accounts:settings')
        else:
            messages.error(request, "Failed to update settings. Please check your input.")
    else:
        form = UserProfileForm(instance=profile)
        # Populate height_feet and height_inches fields if height_unit is imperial
        if profile.height_unit == 'ft_in':
            form.fields['height_feet'].initial = profile.height_feet
            form.fields['height_inches'].initial = profile.height_inches
            
    return render(request, 'accounts/settings.html', {'form': form})

def google_login(request):
    client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    if not client_id or client_id == 'mock-google-client-id':
        # Simulated callback URL for testing/development if no credentials
        messages.warning(request, "Google login is running in simulation mode because GOOGLE_CLIENT_ID is not configured.")
        return redirect('accounts:google_callback_simulation')
        
    redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
    scope = 'openid email profile'
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'prompt': 'select_account',
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return redirect(url)

def google_callback(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, "Google authentication failed: missing authorization code.")
        return redirect('login')
        
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = request.build_absolute_uri(reverse('accounts:google_callback'))
    
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=data)
        response_data = response.json()
        
        if 'error' in response_data:
            messages.error(request, f"Google token exchange failed: {response_data.get('error_description', 'Unknown error')}")
            return redirect('login')
            
        access_token = response_data.get('access_token')
        
        # Fetch user information
        userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo = userinfo_response.json()
        
        email = userinfo.get('email')
        sub = userinfo.get('sub')
        name = userinfo.get('name', '')
        
        if not email:
            messages.error(request, "Google login failed: Email not provided by Google account.")
            return redirect('login')
            
        # Create or retrieve user
        user = CustomUser.objects.filter(google_id=sub).first()
        if not user:
            user = CustomUser.objects.filter(email=email).first()
            if user:
                user.google_id = sub
                user.save()
            else:
                username = email.split('@')[0]
                base_username = username
                counter = 1
                while CustomUser.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                user = CustomUser.objects.create_user(
                    email=email,
                    username=username,
                    google_id=sub
                )
                profile = user.profile
                profile.name = name
                profile.save()
                
        login(request, user)
        messages.success(request, f"Successfully logged in via Google as {user.username}.")
        if not user.profile.onboarded:
            return redirect('accounts:onboarding')
        return redirect('dashboard:index')
        
    except Exception as e:
        messages.error(request, f"An error occurred during Google OAuth exchange: {str(e)}")
        return redirect('login')

def google_callback_simulation(request):
    """
    Simulated callback view for testing Google login locally without active client keys.
    """
    email = "simulated.user@example.com"
    sub = "simulated_google_sub_id_12345678"
    name = "Simulated Google User"
    
    user = CustomUser.objects.filter(google_id=sub).first()
    if not user:
        user = CustomUser.objects.filter(email=email).first()
        if user:
            user.google_id = sub
            user.save()
        else:
            user = CustomUser.objects.create_user(
                email=email,
                username="simulated_user",
                google_id=sub
            )
            profile = user.profile
            profile.name = name
            profile.save()
            
    login(request, user)
    messages.success(request, "[DEMO MODE] Successfully logged in using Google simulation.")
    if not user.profile.onboarded:
        return redirect('accounts:onboarding')
    return redirect('dashboard:index')
