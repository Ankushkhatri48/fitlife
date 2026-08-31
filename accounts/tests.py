from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import UserProfile
from accounts.services import convert_to_metric, calculate_daily_targets
from decimal import Decimal

User = get_user_model()

class AccountsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123"
        )
        
    def test_profile_auto_created(self):
        """Test that registering a user automatically builds their profile."""
        self.assertIsNotNone(self.user.profile)
        self.assertEqual(self.user.profile.user, self.user)
        self.assertFalse(self.user.profile.onboarded)
        
    def test_metric_conversions(self):
        """Test metric units converter (lb to kg, ft_in to cm)."""
        # 1. lbs to kg
        kg, cm = convert_to_metric(weight=150, weight_unit='lb', height_cm=180, height_unit='cm')
        self.assertAlmostEqual(float(kg), 150 * 0.45359237)
        self.assertEqual(float(cm), 180.0)
        
        # 2. ft/in to cm
        kg, cm = convert_to_metric(weight=70, weight_unit='kg', height_feet=5, height_inches=9, height_unit='ft_in')
        self.assertEqual(float(kg), 70.0)
        self.assertAlmostEqual(float(cm), (5 * 12 + 9) * 2.54)
        
    def test_daily_calorie_target_estimation_male(self):
        """Test calorie calculation Mifflin-St Jeor for Male (Active)."""
        profile = self.user.profile
        profile.age = 25
        profile.gender = 'Male'
        profile.weight = 80
        profile.weight_unit = 'kg'
        profile.height = 180
        profile.height_unit = 'cm'
        profile.activity_level = 'Moderately active'
        profile.goal = 'Maintain weight'
        profile.save()
        
        # BMR Male = 10 * 80 + 6.25 * 180 - 5 * 25 + 5 = 800 + 1125 - 125 + 5 = 1805
        # TDEE = 1805 * 1.55 = 2797.75 ≈ 2798
        targets = calculate_daily_targets(profile)
        self.assertEqual(targets['bmr'], 1805)
        self.assertEqual(targets['tdee'], 2798)
        self.assertEqual(targets['calories'], 2798)
        
    def test_daily_calorie_target_estimation_female(self):
        """Test Mifflin-St Jeor BMR for Female (Lose Weight)."""
        profile = self.user.profile
        profile.age = 30
        profile.gender = 'Female'
        profile.weight = 60
        profile.weight_unit = 'kg'
        profile.height = 165
        profile.height_unit = 'cm'
        profile.activity_level = 'Sedentary'
        profile.goal = 'Lose weight'
        profile.save()
        
        # BMR Female = 10 * 60 + 6.25 * 165 - 5 * 30 - 161 = 600 + 1031.25 - 150 - 161 = 1320.25
        # TDEE = 1320.25 * 1.2 = 1584.3
        # Deficit calories = 1584.3 - 500 = 1084.3 -> capped at 1200 as sensible limit
        targets = calculate_daily_targets(profile)
        self.assertEqual(targets['bmr'], 1320)
        self.assertEqual(targets['calories'], 1200) # checks capping logic
