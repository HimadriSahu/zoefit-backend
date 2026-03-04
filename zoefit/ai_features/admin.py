"""
AI Features Admin Configuration

This module configures the Django admin interface for AI features models.
"""

from django.contrib import admin
from .models import (
    HealthMetrics, MealPlan, WorkoutPlan, 
    AIChatHistory, ProgressTracking
)


@admin.register(HealthMetrics)
class HealthMetricsAdmin(admin.ModelAdmin):
    """
    Admin configuration for HealthMetrics model.
    """
    list_display = [
        'user', 'height', 'weight', 'bmi', 'fitness_goal', 
        'activity_level', 'created_at', 'updated_at'
    ]
    list_filter = [
        'fitness_goal', 'activity_level', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['bmi', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Physical Measurements', {
            'fields': ('height', 'weight', 'bmi')
        }),
        ('Fitness Profile', {
            'fields': ('fitness_goal', 'activity_level', 'target_weight')
        }),
        ('Health Information', {
            'fields': ('dietary_preferences', 'medical_conditions', 'allergies')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    """
    Admin configuration for MealPlan model.
    """
    list_display = [
        'user', 'date', 'total_calories', 'protein', 'carbs', 'fat',
        'generated_by_ai', 'confidence_score', 'user_rating'
    ]
    list_filter = [
        'date', 'generated_by_ai', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date')
        }),
        ('Nutritional Information', {
            'fields': ('total_calories', 'protein', 'carbs', 'fat')
        }),
        ('AI Metadata', {
            'fields': ('generated_by_ai', 'confidence_score')
        }),
        ('User Feedback', {
            'fields': ('user_rating', 'user_feedback')
        }),
        ('Meal Data', {
            'fields': ('meals',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    """
    Admin configuration for WorkoutPlan model.
    """
    list_display = [
        'user', 'day', 'workout_type', 'estimated_duration',
        'difficulty_level', 'intensity_score', 'completed', 'user_rating'
    ]
    list_filter = [
        'workout_type', 'difficulty_level', 'completed', 'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'day', 'workout_type')
        }),
        ('Workout Details', {
            'fields': ('estimated_duration', 'difficulty_level', 'intensity_score')
        }),
        ('Equipment & AI', {
            'fields': ('equipment_needed', 'generated_by_ai', 'adaptation_score')
        }),
        ('Completion Data', {
            'fields': ('completed', 'completion_time', 'user_rating')
        }),
        ('Exercise Data', {
            'fields': ('exercises',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(AIChatHistory)
class AIChatHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for AIChatHistory model.
    """
    list_display = [
        'user', 'intent_detected', 'confidence_score', 'helpful', 'created_at'
    ]
    list_filter = [
        'intent_detected', 'helpful', 'created_at'
    ]
    search_fields = ['user__username', 'user_message', 'ai_response']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Conversation Data', {
            'fields': ('user_message', 'ai_response')
        }),
        ('AI Analysis', {
            'fields': ('intent_detected', 'confidence_score')
        }),
        ('User Feedback', {
            'fields': ('helpful',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )


@admin.register(ProgressTracking)
class ProgressTrackingAdmin(admin.ModelAdmin):
    """
    Admin configuration for ProgressTracking model.
    """
    list_display = [
        'user', 'weight', 'body_fat_percentage', 'workout_streak',
        'total_workouts', 'progress_score', 'created_at'
    ]
    list_filter = [
        'created_at'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Physical Measurements', {
            'fields': ('weight', 'body_fat_percentage', 'muscle_mass')
        }),
        ('Performance Metrics', {
            'fields': ('workout_streak', 'total_workouts', 'calories_burned')
        }),
        ('AI Analysis', {
            'fields': ('progress_score', 'achievement_badges', 'ai_insights')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )
