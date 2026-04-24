"""
Django signals for automatic data synchronization in users module
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=UserProfile)
def sync_user_profile_to_health_metrics(sender, instance, created, **kwargs):
    """
    Automatically sync UserProfile data to HealthMetrics when UserProfile is saved.
    This ensures ML engine always has access to the latest user data.
    """
    try:
        # Import here to avoid circular imports
        from ai_features.models import HealthMetrics
        
        # Calculate BMI if we have both height and weight
        bmi = None
        if instance.height and instance.weight:
            height_in_meters = float(instance.height) / 100
            bmi = round(float(instance.weight) / (height_in_meters ** 2), 2)
        
        # Get or create HealthMetrics
        health_metrics, created = HealthMetrics.objects.get_or_create(
            user=instance.user,
            defaults={
                'height': instance.height,
                'weight': instance.weight,
                'bmi': bmi,
                'fitness_goal': instance.fitness_goal or 'maintenance',
                'activity_level': instance.activity_level or 'moderate',
                'dietary_preferences': instance.dietary_preferences or {},
                'medical_conditions': instance.medical_conditions or [],
                'allergies': instance.allergies or [],
                'target_weight': instance.target_weight,
            }
        )
        
        if not created:
            # Update existing HealthMetrics with profile data
            health_metrics.height = instance.height
            health_metrics.weight = instance.weight
            health_metrics.fitness_goal = instance.fitness_goal or health_metrics.fitness_goal
            health_metrics.activity_level = instance.activity_level or health_metrics.activity_level
            health_metrics.dietary_preferences = instance.dietary_preferences or health_metrics.dietary_preferences
            health_metrics.medical_conditions = instance.medical_conditions or health_metrics.medical_conditions
            health_metrics.allergies = instance.allergies or health_metrics.allergies
            health_metrics.target_weight = instance.target_weight or health_metrics.target_weight
            
            # Auto-calculate BMI if we have height and weight
            if health_metrics.height and health_metrics.weight:
                health_metrics.bmi = health_metrics.calculate_bmi()
        
        health_metrics.save()
        
    except Exception as e:
        # Log error but don't fail the save operation
        print(f"Error auto-syncing profile to health metrics: {e}")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create UserProfile when a new User is created.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
