"""
Django admin configuration for frontend module.

This module configures the Django admin interface for frontend models,
providing an intuitive interface for managing user data, monitoring
progress, and analyzing fitness trends.

Key features:
- Comprehensive model representations
- Search and filtering capabilities
- Inline editing for related data
- Custom admin actions for common tasks
- Data export functionality
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum, Avg
from django.utils.safestring import mark_safe

from .models import (
    WorkoutSession, ExerciseLog, ProgressSnapshot,
    Streak, MealLog, Achievement
)


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    """Admin configuration for WorkoutSession model."""
    
    list_display = [
        'user', 'start_time', 'duration_display', 'completed',
        'calories_burned', 'difficulty_rating', 'workout_plan_link'
    ]
    list_filter = [
        'completed', 'difficulty_rating', 'start_time',
        'workout_plan', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'user_notes'
    ]
    date_hierarchy = 'start_time'
    readonly_fields = ['created_at', 'updated_at', 'duration']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'workout_plan', 'start_time', 'end_time', 'duration')
        }),
        ('Workout Details', {
            'fields': ('completed', 'exercises_completed', 'calories_burned')
        }),
        ('User Feedback', {
            'fields': ('difficulty_rating', 'user_notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def duration_display(self, obj):
        """Display duration in a readable format."""
        if obj.duration:
            total_seconds = int(obj.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "Not set"
    duration_display.short_description = 'Duration'
    
    def workout_plan_link(self, obj):
        """Display workout plan as a clickable link if available."""
        if obj.workout_plan:
            return format_html(
                '<a href="/admin/ai_features/workoutplan/{}/change/">Day {}</a>',
                obj.workout_plan.id,
                obj.workout_plan.day
            )
        return "No plan"
    workout_plan_link.short_description = 'Workout Plan'
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('user', 'workout_plan')


class ExerciseLogInline(admin.TabularInline):
    """Inline admin for ExerciseLog within WorkoutSession."""
    
    model = ExerciseLog
    extra = 0
    fields = [
        'exercise_name', 'sets_completed', 'reps_per_set',
        'weight_used', 'rest_time', 'form_rating'
    ]
    readonly_fields = ['created_at']


# Update WorkoutSessionAdmin to include inline
WorkoutSessionAdmin.inlines = [ExerciseLogInline]


@admin.register(ExerciseLog)
class ExerciseLogAdmin(admin.ModelAdmin):
    """Admin configuration for ExerciseLog model."""
    
    list_display = [
        'exercise_name', 'workout_session_link', 'sets_completed',
        'weight_used', 'form_rating', 'created_at'
    ]
    list_filter = [
        'exercise_name', 'form_rating', 'created_at'
    ]
    search_fields = [
        'exercise_name', 'workout_session__user__username',
        'workout_session__user__email', 'notes'
    ]
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    def workout_session_link(self, obj):
        """Display workout session as a clickable link."""
        return format_html(
            '<a href="/admin/frontend/workoutsession/{}/change/">{} - {}</a>',
            obj.workout_session.id,
            obj.workout_session.user.username,
            obj.workout_session.start_time.strftime('%Y-%m-%d')
        )
    workout_session_link.short_description = 'Workout Session'
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('workout_session__user')


@admin.register(ProgressSnapshot)
class ProgressSnapshotAdmin(admin.ModelAdmin):
    """Admin configuration for ProgressSnapshot model."""
    
    list_display = [
        'user', 'date', 'weight', 'body_fat_percentage',
        'muscle_mass', 'measurement_count', 'created_at'
    ]
    list_filter = [
        'date', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'notes'
    ]
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'date')
        }),
        ('Physical Measurements', {
            'fields': ('weight', 'body_fat_percentage', 'muscle_mass')
        }),
        ('Body Measurements', {
            'fields': ('measurements', 'progress_photos')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def measurement_count(self, obj):
        """Display count of body measurements."""
        return len(obj.measurements) if obj.measurements else 0
    measurement_count.short_description = 'Measurements'
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('user')


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    """Admin configuration for Streak model."""
    
    list_display = [
        'user', 'streak_type_display', 'current_count',
        'longest_count', 'is_active', 'last_activity_date',
        'days_since_activity'
    ]
    list_filter = [
        'streak_type', 'is_active', 'last_activity_date'
    ]
    search_fields = [
        'user__username', 'user__email'
    ]
    date_hierarchy = 'last_activity_date'
    readonly_fields = ['created_at', 'updated_at']
    
    def streak_type_display(self, obj):
        """Display formatted streak type."""
        return obj.get_streak_type_display()
    streak_type_display.short_description = 'Streak Type'
    
    def days_since_activity(self, obj):
        """Calculate days since last activity."""
        from django.utils import timezone
        delta = timezone.now().date() - obj.last_activity_date
        return delta.days
    days_since_activity.short_description = 'Days Since Activity'
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('user')


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    """Admin configuration for MealLog model."""
    
    list_display = [
        'user', 'meal_type_display', 'meal_time',
        'total_calories', 'protein_carbs_fat', 'food_items_count'
    ]
    list_filter = [
        'meal_type', 'meal_time', 'created_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'notes'
    ]
    date_hierarchy = 'meal_time'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'meal_type', 'meal_time')
        }),
        ('Nutritional Information', {
            'fields': ('food_items', 'total_calories', 'protein', 'carbs', 'fat')
        }),
        ('Additional Information', {
            'fields': ('photo_url', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def meal_type_display(self, obj):
        """Display formatted meal type."""
        return obj.get_meal_type_display()
    meal_type_display.short_description = 'Meal Type'
    
    def protein_carbs_fat(self, obj):
        """Display macros in a compact format."""
        return f"P:{obj.protein}g C:{obj.carbs}g F:{obj.fat}g"
    protein_carbs_fat.short_description = 'Macros'
    
    def food_items_count(self, obj):
        """Display count of food items."""
        return len(obj.food_items) if obj.food_items else 0
    food_items_count.short_description = 'Food Items'
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('user')


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    """Admin configuration for Achievement model."""
    
    list_display = [
        'user', 'title', 'achievement_type', 'points_awarded',
        'is_displayed', 'earned_date'
    ]
    list_filter = [
        'achievement_type', 'is_displayed', 'earned_date'
    ]
    search_fields = [
        'user__username', 'user__email', 'title', 'description'
    ]
    date_hierarchy = 'earned_date'
    readonly_fields = ['earned_date']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Achievement Details', {
            'fields': ('achievement_type', 'title', 'description', 'badge_icon')
        }),
        ('Points and Display', {
            'fields': ('points_awarded', 'is_displayed', 'earned_date')
        })
    )
    
    def get_queryset(self, request):
        """Optimize queries with select_related."""
        return super().get_queryset(request).select_related('user')


# Custom admin actions
@admin.action(description='Mark selected workouts as completed')
def mark_workouts_completed(modeladmin, request, queryset):
    """Mark selected workout sessions as completed."""
    updated = queryset.update(completed=True)
    modeladmin.message_user(request, f'{updated} workouts marked as completed.')


@admin.action(description='Reset selected streaks')
def reset_streaks(modeladmin, request, queryset):
    """Reset selected streaks to zero."""
    updated = queryset.update(current_count=0, is_active=False)
    modeladmin.message_user(request, f'{updated} streaks reset.')


@admin.action(description='Toggle achievement display status')
def toggle_achievement_display(modeladmin, request, queryset):
    """Toggle display status for selected achievements."""
    for achievement in queryset:
        achievement.is_displayed = not achievement.is_displayed
        achievement.save()
    modeladmin.message_user(request, f'Display status toggled for {queryset.count()} achievements.')


# Add actions to respective admin classes
WorkoutSessionAdmin.actions = [mark_workouts_completed]
StreakAdmin.actions = [reset_streaks]
AchievementAdmin.actions = [toggle_achievement_display]


# Admin site customization
admin.site.site_header = 'ZoeFit Administration'
admin.site.site_title = 'ZoeFit Admin'
admin.site.index_title = 'Welcome to ZoeFit Administration'
