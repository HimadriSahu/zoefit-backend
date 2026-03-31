"""
AI Features Admin Configuration

This module configures the Django admin interface for AI features models.
"""

from django.contrib import admin
from .models import (
    HealthMetrics, AIChatHistory, ProgressTracking
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
