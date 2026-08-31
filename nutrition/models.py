from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class DailyNutritionEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutrition_entries'
    )
    date = models.DateField()
    
    # Mandatory fields
    calories = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Calories (kcal)"
    )
    protein = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Protein (grams)"
    )
    
    # Optional fields
    carbohydrates = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Carbohydrates (grams)"
    )
    fat = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Fat (grams)"
    )
    fiber = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Fiber (grams)"
    )
    sugar = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Sugar (grams)"
    )
    sodium = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Sodium (mg)"
    )
    water = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Water (ml)"
    )
    caffeine = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Caffeine (mg)"
    )
    
    notes = models.TextField(blank=True, help_text="What you ate / workouts / comments")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.email} - {self.date}: {self.calories} kcal"
