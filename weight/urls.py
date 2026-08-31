from django.urls import path
from weight import views

app_name = 'weight'

urlpatterns = [
    path('log/', views.log_weight_view, name='log_weight'),
    path('delete/<int:pk>/', views.delete_weight_view, name='delete_weight'),
    path('history/', views.history_weight_view, name='history'),
]
