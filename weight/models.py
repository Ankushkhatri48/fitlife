from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class WeightLog(models.Model):
    UNIT_CHOICES = [
        ('kg', 'kg'),
        ('lb', 'lb'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weight_logs'
    )
    date = models.DateField()
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.1'))],
        help_text="Weight log value"
    )
    unit = models.CharField(
        max_length=5,
        choices=UNIT_CHOICES,
        default='kg'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.weight} {self.unit}"
