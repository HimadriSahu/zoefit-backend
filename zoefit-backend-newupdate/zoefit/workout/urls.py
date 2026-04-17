"""
URL patterns for workout module

This file defines all workout-related endpoints:
- Workout plan generation and management
- Workout preferences and equipment
- Workout session tracking and completion
- Workout progress and performance analytics

These URLs are organized to provide a clean, intuitive API
structure specifically for workout functionality.
"""

from django.urls import path
from . import views

app_name = 'workout'

urlpatterns = [
    # Workout Plan Management
    path('plans/generate/', views.generate_workout_plan, name='generate_workout_plan'),
    path('plans/', views.get_workout_plans, name='get_workout_plans'),
    path('plans/adapt/', views.adapt_workout_plan, name='adapt_workout_plan'),
    
    # Workout Sessions
    path('sessions/', views.get_workout_sessions, name='get_workout_sessions'),
    path('complete/', views.update_workout_completion, name='update_workout_completion'),
    
    # Workout Progress
    path('progress/', views.get_workout_progress, name='get_workout_progress'),
]
