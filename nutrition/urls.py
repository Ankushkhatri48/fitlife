from django.urls import path
from nutrition import views

app_name = 'nutrition'

urlpatterns = [
    path('log/', views.log_entry_view, name='log_entry'),
    path('delete/<int:pk>/', views.delete_entry_view, name='delete_entry'),
    path('history/', views.history_view, name='history'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calculator/calorie/', views.calorie_calculator_view, name='calorie_calculator'),
    path('calculator/caffeine/', views.caffeine_calculator_view, name='caffeine_calculator'),
    path('calculator/sugar/', views.sugar_calculator_view, name='sugar_calculator'),
]
