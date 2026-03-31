"""
URL patterns for nutrition module

This file defines all nutrition-related endpoints:
- Meal plan generation and management
- Dietary preferences and restrictions
- Nutrition tracking and logging
- Nutrition progress and analytics

These URLs are organized to provide a clean, intuitive API
structure specifically for nutrition functionality.
"""

from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    # Meal Plan Management
    path('meal-plans/generate/', views.generate_meal_plan, name='generate_meal_plan'),
    path('meal-plans/', views.get_meal_plans, name='get_meal_plans'),
    
    # Dietary Preferences
    path('preferences/', views.save_dietary_preferences, name='save_dietary_preferences'),
    path('preferences/get/', views.get_dietary_preferences, name='get_dietary_preferences'),
    
    # Nutrition Logging
    path('logs/', views.get_nutrition_logs, name='get_nutrition_logs'),
    path('logs/log/', views.log_nutrition, name='log_nutrition'),
    
    # Nutrition Progress
    path('progress/', views.get_nutrition_progress, name='get_nutrition_progress'),
    path('progress/update/', views.update_nutrition_progress, name='update_nutrition_progress'),
    
    # Food Database
    path('foods/search/', views.search_foods, name='search_foods'),
]
