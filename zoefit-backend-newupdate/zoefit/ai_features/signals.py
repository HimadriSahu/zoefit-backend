"""
Signals for automatic data synchronization between modules.

These signals ensure that ProgressTracking is automatically updated
when relevant data changes in workout or nutrition modules.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ProgressTracking
from workout.models import WorkoutPlan, WorkoutSession, WorkoutProgress
from nutrition.models import MealPlan, NutritionLog, NutritionProgress
from .services import ProgressSyncService

User = get_user_model()


@receiver(post_save, sender=WorkoutPlan)
def workout_plan_updated(sender, instance, created, **kwargs):
    """
    Update ProgressTracking when a workout plan is created or updated.
    """
    try:
        if created or instance.completed != kwargs.get('update_fields', []):
            ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in workout_plan_updated signal: {e}")


@receiver(post_save, sender=WorkoutSession)
def workout_session_updated(sender, instance, created, **kwargs):
    """
    Update ProgressTracking when a workout session is completed.
    """
    try:
        if instance.completed:
            ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in workout_session_updated signal: {e}")


@receiver(post_save, sender=WorkoutProgress)
def workout_progress_updated(sender, instance, created, **kwargs):
    """
    Update ProgressTracking when workout progress is updated.
    """
    try:
        ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in workout_progress_updated signal: {e}")


@receiver(post_save, sender=MealPlan)
def meal_plan_updated(sender, instance, created, **kwargs):
    """
    Update ProgressTracking when a meal plan is created or updated.
    """
    try:
        ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in meal_plan_updated signal: {e}")


@receiver(post_save, sender=NutritionLog)
def nutrition_log_updated(sender, instance, created, **kwargs):
    """
    Update ProgressTracking when a nutrition log is created or updated.
    """
    try:
        ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in nutrition_log_updated signal: {e}")


@receiver(post_save, sender=NutritionProgress)
def nutrition_progress_updated(sender, instance, created, **kwargs):
    """
    Update ProgressTracking when nutrition progress is updated.
    """
    try:
        ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in nutrition_progress_updated signal: {e}")


@receiver(post_delete, sender=WorkoutSession)
def workout_session_deleted(sender, instance, **kwargs):
    """
    Update ProgressTracking when a workout session is deleted.
    """
    try:
        ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in workout_session_deleted signal: {e}")


@receiver(post_delete, sender=NutritionLog)
def nutrition_log_deleted(sender, instance, **kwargs):
    """
    Update ProgressTracking when a nutrition log is deleted.
    """
    try:
        ProgressSyncService.update_user_progress(instance.user)
    except Exception as e:
        print(f"Error in nutrition_log_deleted signal: {e}")


# Connect signals when Django app is ready
def connect_signals():
    """
    Connect all signals. This function should be called in the app's ready() method.
    """
    pass  # Signals are automatically connected when this module is imported
