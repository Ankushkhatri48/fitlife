from django.contrib import admin
from nutrition.models import DailyNutritionEntry

class DailyNutritionEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'calories', 'protein', 'carbohydrates', 'fat', 'sugar', 'caffeine')
    list_filter = ('date',)
    search_fields = ('user__email', 'user__username', 'notes')
    ordering = ('-date',)

admin.site.register(DailyNutritionEntry, DailyNutritionEntryAdmin)
