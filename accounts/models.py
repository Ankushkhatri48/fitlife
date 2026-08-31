from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    # We want users to be able to log in with email as the primary identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    ]
    
    UNIT_WEIGHT_CHOICES = [
        ('kg', 'kg'),
        ('lb', 'lb'),
    ]
    
    UNIT_HEIGHT_CHOICES = [
        ('cm', 'cm'),
        ('ft_in', 'ft/in'),
    ]
    
    GOAL_CHOICES = [
        ('Lose weight', 'Lose weight'),
        ('Maintain weight', 'Maintain weight'),
        ('Gain weight', 'Gain weight'),
    ]
    
    ACTIVITY_CHOICES = [
        ('Sedentary', 'Sedentary (little or no exercise)'),
        ('Lightly active', 'Lightly active (light exercise/sports 1-3 days/week)'),
        ('Moderately active', 'Moderately active (moderate exercise/sports 3-5 days/week)'),
        ('Very active', 'Very active (hard exercise/sports 6-7 days/week)'),
        ('Extremely active', 'Extremely active (very hard exercise/physical job)'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=150, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Prefer not to say')
    
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True) # in cm, or feet (will convert in view)
    height_feet = models.PositiveIntegerField(null=True, blank=True)
    height_inches = models.PositiveIntegerField(null=True, blank=True)
    
    weight_unit = models.CharField(max_length=5, choices=UNIT_WEIGHT_CHOICES, default='kg')
    height_unit = models.CharField(max_length=10, choices=UNIT_HEIGHT_CHOICES, default='cm')
    
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='Maintain weight')
    activity_level = models.CharField(max_length=30, choices=ACTIVITY_CHOICES, default='Sedentary')
    
    # Target Overrides & Settings
    daily_calorie_target_override = models.PositiveIntegerField(null=True, blank=True)
    protein_target_override = models.PositiveIntegerField(null=True, blank=True)
    carbs_target_override = models.PositiveIntegerField(null=True, blank=True)
    fat_target_override = models.PositiveIntegerField(null=True, blank=True)
    
    timezone = models.CharField(max_length=50, default='UTC')
    onboarded = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
