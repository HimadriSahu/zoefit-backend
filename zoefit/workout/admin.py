"""
Admin configuration for workout module
"""

from django.contrib import admin
from .models import WorkoutPlan, WorkoutSession, WorkoutProgress


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'day', 'workout_type', 'difficulty_level', 'completed', 'created_at']
    list_filter = ['workout_type', 'difficulty_level', 'completed', 'created_at']
    search_fields = ['user__username', 'workout_type']
    readonly_fields = ['created_at']
    ordering = ['-created_at']




@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'workout_plan', 'workout_type', 'completed', 'start_time', 'duration']
    list_filter = ['workout_type', 'completed', 'start_time']
    search_fields = ['user__username', 'workout_type']
    readonly_fields = ['created_at']
    ordering = ['-start_time']


@admin.register(WorkoutProgress)
class WorkoutProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_workouts', 'workout_streak', 'performance_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
