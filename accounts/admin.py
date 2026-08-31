from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'
    fk_name = 'user'
    exclude = ['google_id'] # avoid exposing sensitive OAuth values

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('email', 'username', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'gender', 'age', 'weight', 'weight_unit', 'height', 'height_unit', 'goal', 'activity_level')
    search_fields = ('user__email', 'user__username', 'name')
    list_filter = ('gender', 'goal', 'activity_level')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
