"""
Nutrition module configuration for ZoeFit
"""

from django.apps import AppConfig


class NutritionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nutrition'
    verbose_name = 'Nutrition Management'
    
    def ready(self):
        """
        Initialize the nutrition module when Django starts.
        """
        pass
