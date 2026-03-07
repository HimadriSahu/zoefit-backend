"""
URL configuration for frontend module.

This module defines the URL patterns for all frontend API endpoints.
The URLs are organized by feature area for clarity and maintainability.

URL structure:
/api/frontend/workout-sessions/     - Workout session management
/api/frontend/progress-snapshots/    - Progress tracking
/api/frontend/streaks/              - Streak tracking
/api/frontend/meal-logs/            - Meal logging
/api/frontend/dashboard/            - Dashboard data
/api/frontend/achievements/          - Achievement system

All endpoints require JWT authentication and follow RESTful conventions.
"""

from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    # Workout History URLs
    path('workout-sessions/', views.workout_sessions_view, name='workout_sessions'),
    path('workout-sessions/<int:session_id>/', views.workout_session_detail_view, name='workout_session_detail'),
    path('workout-stats/', views.workout_stats_view, name='workout_stats'),
    
    # Progress Tracking URLs
    path('progress-snapshots/', views.progress_snapshots_view, name='progress_snapshots'),
    path('progress-charts/', views.progress_charts_view, name='progress_charts'),
    
    # Streak Tracking URLs
    path('streaks/', views.streaks_view, name='streaks'),
    path('streak-history/', views.streak_history_view, name='streak_history'),
    
    # Meal Logging URLs
    path('meal-logs/', views.meal_logs_view, name='meal_logs'),
    path('nutrition-summary/', views.nutrition_summary_view, name='nutrition_summary'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_summary_view, name='dashboard_summary'),
    path('daily-stats/', views.daily_stats_view, name='daily_stats'),
    
    # Achievement URLs
    path('achievements/', views.achievements_view, name='achievements'),
]
