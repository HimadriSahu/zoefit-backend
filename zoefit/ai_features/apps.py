"""
AI Features Django App Configuration
"""

from django.apps import AppConfig


class AiFeaturesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_features'
    verbose_name = 'AI Features'
    
    def ready(self):
        """
        Initialize AI features when the app is ready.
        """
        # Import models to ensure they're registered
        from . import models
        
        # Import and connect signals for automatic data synchronization
        try:
            from . import signals
        except ImportError:
            pass  # Signals file may not exist in all environments
