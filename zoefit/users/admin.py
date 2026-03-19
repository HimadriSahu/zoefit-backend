"""
Admin configuration for users module
"""

from django.contrib import admin
from .models import UserProfile, UserActivity


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""
    list_display = [
        'user', 'full_name', 'email', 'fitness_goal', 
        'activity_level', 'onboarding_completed', 'created_at'
    ]
    list_filter = [
        'fitness_goal', 'activity_level', 'onboarding_completed', 
        'gender', 'difficulty_level', 'workout_type_preference'
    ]
    search_fields = ['user__username', 'user__email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at', 'onboarding_completed_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('user', 'first_name', 'last_name', 'phone_number', 
                      'date_of_birth', 'profile_picture', 'bio', 'location')
        }),
        ('Health & Fitness', {
            'fields': ('height', 'weight', 'target_weight', 'fitness_goal', 
                      'activity_level', 'body_fat_percentage', 'muscle_mass')
        }),
        ('Workout Preferences', {
            'fields': ('workout_duration', 'workout_types', 'equipment_available',
                      'difficulty_level', 'workout_type_preference')
        }),
        ('Dietary Information', {
            'fields': ('dietary_preferences', 'allergies', 'medical_conditions')
        }),
        ('Onboarding', {
            'fields': ('gender', 'breakfast_time', 'lunch_time', 'dinner_time',
                      'onboarding_completed', 'onboarding_completed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin configuration for UserActivity model."""
    list_display = ['user', 'activity_type', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'activity_type', 'activity_data', 'timestamp')
        }),
    )
