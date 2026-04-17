"""
Nutrition module models for ZoeFit

This module contains all nutrition-related data models:
- Meal plans and recipes
- Dietary preferences and restrictions
- Nutrition tracking and analytics
- Food database and nutritional information

These models are specifically focused on nutrition functionality
and are separated from workout to create a more modular structure.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MealPlan(models.Model):
    """
    Personalized meal plans created by AI.
    
    Each meal plan is for a specific day and includes:
    - Breakfast, lunch, dinner, and snacks
    - Total calories and macronutrients
    - AI confidence score (how sure we are this plan will work for you)
    
    Users can rate their meal plans and leave feedback.
    This helps our AI learn what works and what doesn't.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meal_plans'
    )
    
    date = models.DateField()
    
    # Meal data stored as JSON
    meals = models.JSONField(
        help_text="Meal data including breakfast, lunch, dinner, snacks"
    )
    
    total_calories = models.IntegerField()
    
    # Macronutrients
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    
    # Micronutrients (optional)
    fiber = models.FloatField(default=0)
    sugar = models.FloatField(default=0)
    sodium = models.FloatField(default=0)
    
    # AI metadata
    generated_by_ai = models.BooleanField(default=True)
    confidence_score = models.FloatField(
        default=0.0,
        help_text="AI confidence in meal plan quality (0-1)"
    )
    
    # User feedback
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="User rating 1-5"
    )
    
    user_feedback = models.TextField(
        blank=True,
        help_text="User feedback on meal plan"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'nutrition_meal_plans'
        verbose_name = 'Meal Plan'
        verbose_name_plural = 'Meal Plans'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username}'s Meal Plan - {self.date}"


class DietaryPreferences(models.Model):
    """
    Stores user dietary preferences and restrictions.
    
    This model captures how users like to eat so our AI can
    create better personalized meal plans.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='dietary_preferences'
    )
    
    # Diet type preferences
    diet_type = models.CharField(
        max_length=50,
        choices=[
            ('omnivore', 'Omnivore'),
            ('vegetarian', 'Vegetarian'),
            ('vegan', 'Vegan'),
            ('pescatarian', 'Pescatarian'),
            ('keto', 'Ketogenic'),
            ('paleo', 'Paleo'),
            ('mediterranean', 'Mediterranean'),
            ('low_carb', 'Low Carb'),
            ('low_fat', 'Low Fat'),
            ('gluten_free', 'Gluten-Free'),
        ],
        default='omnivore',
        help_text="Primary diet type preference"
    )
    
    # Dietary restrictions (JSON array)
    restrictions = models.JSONField(
        default=list,
        help_text="List of dietary restrictions (e.g., lactose-free, nut-free)"
    )
    
    # Allergies (JSON array)
    allergies = models.JSONField(
        default=list,
        help_text="List of food allergies"
    )
    
    # Food dislikes (JSON array)
    disliked_foods = models.JSONField(
        default=list,
        help_text="List of foods user dislikes"
    )
    
    # Preferred foods (JSON array)
    preferred_foods = models.JSONField(
        default=list,
        help_text="List of foods user prefers"
    )
    
    # Meal timing preferences
    meals_per_day = models.IntegerField(
        default=3,
        help_text="Number of meals preferred per day"
    )
    
    snack_frequency = models.CharField(
        max_length=20,
        choices=[
            ('never', 'Never'),
            ('rarely', 'Rarely'),
            ('sometimes', 'Sometimes'),
            ('daily', 'Daily'),
            ('multiple', 'Multiple times per day'),
        ],
        default='sometimes',
        help_text="How often user prefers snacks"
    )
    
    # Calorie and macro preferences
    target_calories = models.IntegerField(
        null=True,
        blank=True,
        help_text="Target daily calories (calculated automatically if not set)"
    )
    
    macro_split = models.JSONField(
        default=dict,
        help_text="Preferred macronutrient split as percentages"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nutrition_dietary_preferences'
        verbose_name = 'Dietary Preferences'
        verbose_name_plural = 'Dietary Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Dietary Preferences"


class NutritionLog(models.Model):
    """
    Tracks user's daily nutrition intake.
    
    This model captures what users actually eat, allowing
    for comparison with planned meals and progress tracking.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='nutrition_logs'
    )
    
    date = models.DateField()
    
    # Meal entries (JSON array of food items with quantities)
    breakfast = models.JSONField(
        default=list,
        help_text="Breakfast food items and quantities"
    )
    
    lunch = models.JSONField(
        default=list,
        help_text="Lunch food items and quantities"
    )
    
    dinner = models.JSONField(
        default=list,
        help_text="Dinner food items and quantities"
    )
    
    snacks = models.JSONField(
        default=list,
        help_text="Snack food items and quantities"
    )
    
    # Daily totals
    total_calories = models.IntegerField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    
    # Water intake
    water_intake_ml = models.IntegerField(
        default=0,
        help_text="Daily water intake in milliliters"
    )
    
    # User notes
    notes = models.TextField(
        blank=True,
        help_text="User notes about the day's nutrition"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nutrition_logs'
        verbose_name = 'Nutrition Log'
        verbose_name_plural = 'Nutrition Logs'
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username}'s Nutrition Log - {self.date}"


class NutritionProgress(models.Model):
    """
    Tracks nutrition-specific progress and metrics.
    
    This model focuses on nutrition trends,
    dietary adherence, and health improvements.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='nutrition_progress'
    )
    
    # Weight and body composition
    weight = models.FloatField(
        null=True,
        blank=True,
        help_text="Weight in kg"
    )
    
        
    # Nutrition adherence metrics
    meal_plan_adherence = models.FloatField(
        default=0.0,
        help_text="Percentage of meals followed as planned (0-100)"
    )
    
    calorie_consistency = models.FloatField(
        default=0.0,
        help_text="How consistent calorie intake is with targets (0-100)"
    )
    
    macro_balance_score = models.FloatField(
        default=0.0,
        help_text="How well macronutrients are balanced (0-100)"
    )
    
    # Health metrics
    blood_pressure_systolic = models.IntegerField(
        null=True,
        blank=True,
        help_text="Systolic blood pressure"
    )
    
    blood_pressure_diastolic = models.IntegerField(
        null=True,
        blank=True,
        help_text="Diastolic blood pressure"
    )
    
    resting_heart_rate = models.IntegerField(
        null=True,
        blank=True,
        help_text="Resting heart rate in bpm"
    )
    
    # AI insights
    nutrition_score = models.FloatField(
        default=0.0,
        help_text="AI-calculated nutrition score (0-100)"
    )
    
    achievement_badges = models.JSONField(
        default=list,
        help_text="List of nutrition-related achievement badges"
    )
    
    ai_insights = models.TextField(
        blank=True,
        help_text="AI-generated nutrition insights and recommendations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'nutrition_progress'
        verbose_name = 'Nutrition Progress'
        verbose_name_plural = 'Nutrition Progress'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Nutrition Progress - {self.created_at.strftime('%Y-%m-%d')}"


class FoodDatabase(models.Model):
    """
    Database of foods with nutritional information.
    
    This model serves as a reference for nutrition calculations
    and meal planning. It can be populated with common foods
    and expanded over time.
    """
    name = models.CharField(
        max_length=200,
        help_text="Food name"
    )
    
    category = models.CharField(
        max_length=100,
        help_text="Food category (e.g., fruits, vegetables, proteins)"
    )
    
    # Nutritional values per 100g
    calories_per_100g = models.IntegerField(
        help_text="Calories per 100g serving"
    )
    
    protein_per_100g = models.FloatField(
        default=0,
        help_text="Protein in grams per 100g"
    )
    
    carbs_per_100g = models.FloatField(
        default=0,
        help_text="Carbohydrates in grams per 100g"
    )
    
    fat_per_100g = models.FloatField(
        default=0,
        help_text="Fat in grams per 100g"
    )
    
    fiber_per_100g = models.FloatField(
        default=0,
        help_text="Fiber in grams per 100g"
    )
    
    sugar_per_100g = models.FloatField(
        default=0,
        help_text="Sugar in grams per 100g"
    )
    
    sodium_per_100g = models.FloatField(
        default=0,
        help_text="Sodium in mg per 100g"
    )
    
    # Additional properties
    is_organic = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    allergens = models.JSONField(
        default=list,
        help_text="List of potential allergens"
    )
    
    # Dietary compatibility
    suitable_for = models.JSONField(
        default=list,
        help_text="List of diet types this food is suitable for"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'nutrition_food_database'
        verbose_name = 'Food Database'
        verbose_name_plural = 'Food Database'
        ordering = ['name']
        unique_together = ['name', 'category']
    
    def __str__(self):
        return f"{self.name} ({self.category})"
