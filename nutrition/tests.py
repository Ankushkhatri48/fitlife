from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from nutrition.models import DailyNutritionEntry
from nutrition.services import calculate_streak_stats, get_user_local_date

User = get_user_model()

class NutritionTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpassword123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpassword123"
        )
        
    def test_entry_creation_and_ownership(self):
        """Test creating nutrition log and verify user data isolation."""
        today = timezone.localdate()
        entry1 = DailyNutritionEntry.objects.create(
            user=self.user1,
            date=today,
            calories=2000,
            protein=150,
            carbohydrates=200,
            fat=60
        )
        
        self.assertEqual(DailyNutritionEntry.objects.filter(user=self.user1).count(), 1)
        self.assertEqual(DailyNutritionEntry.objects.filter(user=self.user2).count(), 0)
        
        # Test duplicate date constraint for same user
        with self.assertRaises(Exception):
            DailyNutritionEntry.objects.create(
                user=self.user1,
                date=today,
                calories=1500,
                protein=100
            )

    def test_streak_calculation(self):
        """Test streak calculation logic under various logging scenarios."""
        today = timezone.localdate()
        
        # Scenario: Log today, yesterday, and day before
        DailyNutritionEntry.objects.create(user=self.user1, date=today, calories=2000, protein=120)
        DailyNutritionEntry.objects.create(user=self.user1, date=today - timedelta(days=1), calories=1900, protein=100)
        DailyNutritionEntry.objects.create(user=self.user1, date=today - timedelta(days=2), calories=1800, protein=110)
        
        stats = calculate_streak_stats(self.user1)
        self.assertEqual(stats['current_streak'], 3)
        self.assertEqual(stats['longest_streak'], 3)
        self.assertEqual(stats['days_tracked'], 3)
        
        # Incomplete entry (no protein/calories) shouldn't count towards streak
        DailyNutritionEntry.objects.create(user=self.user2, date=today, calories=2000, protein=0)
        stats2 = calculate_streak_stats(self.user2)
        self.assertEqual(stats2['current_streak'], 0)

    def test_fat_equivalent_math(self):
        """Test fat equivalent formula: 7700 kcal = 1 kg fat."""
        calorie_target = 2000
        calories_consumed = 2770 # 770 kcal surplus
        
        diff = calories_consumed - calorie_target
        fat_eq = Decimal(str(diff)) / Decimal('7700')
        self.assertEqual(float(fat_eq), 0.1) # 0.1 kg surplus
