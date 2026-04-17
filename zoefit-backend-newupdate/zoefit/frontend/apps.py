"""
Frontend module configuration for ZoeFit

This module handles all user-facing data visualization and tracking features:
- Workout history and logging
- Progress tracking and visualization
- Streak tracking system
- Meal logging and nutrition history
- Dashboard and analytics

The frontend module serves as the bridge between raw data storage
and meaningful user experiences, providing APIs that power the
ZoeFit web and mobile applications.
"""

from django.apps import AppConfig


class FrontendConfig(AppConfig):
    """Django app configuration for the frontend module."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontend'
    verbose_name = 'Frontend Features'
    
    def ready(self):
        """
        Initialize the frontend module when Django starts.
        
        This is where we can set up any signal handlers,
        register custom model managers, or perform other
        initialization tasks for the frontend module.
        """
        # Import signal handlers here if needed
        # from . import signals
        pass
