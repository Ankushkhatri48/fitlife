from django.urls import path
from dashboard import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('dashboard/', views.index_view, name='index'),
    path('progress/', views.progress_view, name='progress'),
]
