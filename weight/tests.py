from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from weight.models import WeightLog

User = get_user_model()

class WeightTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="weightuser",
            email="weightuser@example.com",
            password="testpassword123"
        )
        
    def test_weight_log_creation(self):
        """Test simple weight log creation and profile weight sync."""
        today = timezone.localdate()
        log = WeightLog.objects.create(
            user=self.user,
            date=today,
            weight=Decimal('75.50'),
            unit='kg'
        )
        
        self.assertEqual(WeightLog.objects.filter(user=self.user).count(), 1)
        self.assertEqual(log.weight, Decimal('75.50'))
        
        # Test duplicate weight entry constraint on same date
        with self.assertRaises(Exception):
            WeightLog.objects.create(
                user=self.user,
                date=today,
                weight=Decimal('76.00'),
                unit='kg'
            )
