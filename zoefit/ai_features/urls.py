"""
URL patterns for AI-powered fitness features

This file defines all the endpoints that make ZoeFit smart:
- Health profile management and BMI calculations
- AI-generated meal plans based on dietary needs
- Personalized workout recommendations
- AI chatbot for fitness questions
- Progress tracking and predictive insights
- Advanced analytics and recommendations

The URLs are organized by feature area to make the API
intuitive and easy to navigate. Each endpoint connects
to a specific AI capability.

All endpoints require authentication except where noted,
since AI recommendations are personalized to each user.
"""

from django.urls import path
from . import views

app_name = 'ai_features'

urlpatterns = [
    # Health Profile Management
    path('health-metrics/', views.create_or_update_health_metrics, name='create_health_metrics'),
    path('health-metrics/get/', views.get_health_metrics, name='get_health_metrics'),
    
    # AI Meal Planning
    path('meal-plan/generate/', views.generate_meal_plan, name='generate_meal_plan'),
    path('meal-plans/', views.get_meal_plans, name='get_meal_plans'),
    
    # AI Workout Generation
    path('workout-plan/generate/', views.generate_workout_plan, name='generate_workout_plan'),
    path('workout-plans/', views.get_workout_plans, name='get_workout_plans'),
    path('workout-complete/', views.update_workout_completion, name='update_workout_completion'),
    
    # AI Fitness Assistant
    path('chat/', views.ai_chat, name='ai_chat'),
    path('chat/history/', views.get_chat_history, name='get_chat_history'),
    
    # Progress Tracking and Analytics
    path('progress/', views.get_progress_tracking, name='get_progress_tracking'),
    path('predict-progress/', views.predict_progress, name='predict_progress'),
    path('insights/', views.get_ai_insights, name='get_ai_insights'),
    
    # Advanced AI Features
    path('adapt-workout/', views.adapt_workout_plan, name='adapt_workout_plan'),
    
    # Analytics and Reporting
    path('analytics/user/', views.get_user_analytics, name='get_user_analytics'),
    path('analytics/system/', views.get_system_analytics, name='get_system_analytics'),
]
