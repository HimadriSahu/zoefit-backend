"""
Admin configuration for nutrition module
"""

from django.contrib import admin
from .models import MealPlan, DietaryPreferences, NutritionLog, NutritionProgress, FoodDatabase


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_calories', 'user_rating', 'created_at']
    list_filter = ['date', 'user_rating', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    ordering = ['-date']


@admin.register(DietaryPreferences)
class DietaryPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'diet_type', 'meals_per_day', 'snack_frequency']
    list_filter = ['diet_type', 'meals_per_day', 'snack_frequency']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NutritionLog)
class NutritionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_calories', 'water_intake_ml']
    list_filter = ['date']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']


@admin.register(NutritionProgress)
class NutritionProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight', 'nutrition_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(FoodDatabase)
class FoodDatabaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g']
    list_filter = ['category', 'is_organic', 'is_processed']
    search_fields = ['name', 'category']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
