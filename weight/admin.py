from django.contrib import admin
from weight.models import WeightLog

class WeightLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'weight', 'unit')
    list_filter = ('date', 'unit')
    search_fields = ('user__email', 'user__username')
    ordering = ('-date',)

admin.site.register(WeightLog, WeightLogAdmin)
