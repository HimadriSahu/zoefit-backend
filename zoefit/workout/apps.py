"""
Workout module configuration for ZoeFit
"""

from django.apps import AppConfig


class WorkoutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workout'
    verbose_name = 'Workout Management'
    
    def ready(self):
        """
        Initialize the workout module when Django starts.
        """
        pass
