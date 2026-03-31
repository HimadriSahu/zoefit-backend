"""
Core AI features models for ZoeFit

This module contains the core AI models that are shared across
workout and nutrition modules:
- Health metrics and profile data
- AI chat history and conversations
- General progress tracking

Workout-specific and nutrition-specific models have been moved
to their respective modules for better separation of concerns.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class HealthMetrics(models.Model):
    """
    Stores each user's health and fitness profile.
    
    This is the foundation of our AI system - everything we recommend
    starts with understanding who the user is and what they want to achieve.
    
    We collect the basics: height, weight, goals, and activity level.
    The AI uses this to calculate things like BMI, daily calorie needs,
    and what kind of workout plan would work best.
    
    Medical conditions and allergies are stored as JSON so we can be
    flexible about what we track without changing the database schema.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='health_metrics'
    )
    
    # Physical Measurements
    height = models.FloatField(
        help_text="Height in centimeters"
    )
    weight = models.FloatField(
        help_text="Weight in kilograms"
    )
    bmi = models.FloatField(
        help_text="Body Mass Index"
    )
    
    # Fitness Goals
    fitness_goal = models.CharField(
        max_length=50,
        choices=[
            ('weight_loss', 'Weight Loss'),
            ('muscle_gain', 'Muscle Gain'),
            ('maintenance', 'Maintenance'),
            ('endurance', 'Endurance'),
            ('strength', 'Strength Building'),
        ],
        default='maintenance'
    )
    
    # Activity Level
    activity_level = models.CharField(
        max_length=30,
        choices=[
            ('sedentary', 'Sedentary - Little or no exercise'),
            ('light', 'Light - Exercise 1-3 days/week'),
            ('moderate', 'Moderate - Exercise 3-5 days/week'),
            ('active', 'Active - Exercise 6-7 days/week'),
            ('very_active', 'Very Active - Physical job or training twice/day'),
        ],
        default='moderate'
    )
    
    # Dietary Preferences (JSON format)
    dietary_preferences = models.JSONField(
        default=dict,
        help_text="Dietary restrictions and preferences"
    )
    
    # Medical Conditions (JSON array)
    medical_conditions = models.JSONField(
        default=list,
        help_text="List of medical conditions"
    )
    
    # Allergies (JSON array)
    allergies = models.JSONField(
        default=list,
        help_text="List of food allergies"
    )
    
    # Target Metrics
    target_weight = models.FloatField(
        null=True,
        blank=True,
        help_text="Target weight in kg"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_health_metrics'
        verbose_name = 'Health Metrics'
        verbose_name_plural = 'Health Metrics'
    
    def __str__(self):
        return f"{self.user.username}'s Health Metrics"
    
    def calculate_bmi(self):
        """
        Calculate Body Mass Index from height and weight.
        
        BMI = weight (kg) / height (m)²
        We round to 2 decimal places for readability.
        
        Returns 0 if we don't have both height and weight.
        """
        if self.height and self.weight:
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters ** 2), 2)
        return 0
    
    def get_bmi_category(self):
        """
        Convert BMI number into a human-readable category.
        
        Uses standard WHO classifications:
        - Underweight: BMI < 18.5
        - Normal: 18.5 ≤ BMI < 25
        - Overweight: 25 ≤ BMI < 30
        - Obese: BMI ≥ 30
        """
        if self.bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= self.bmi < 25:
            return 'Normal'
        elif 25 <= self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def calculate_daily_calories(self):
        """
        Calculate how many calories the user should eat each day.
        
        This is a simplified version of the Harris-Benedict equation:
        1. Calculate Basal Metabolic Rate (BMR) - calories at rest
        2. Multiply by activity level to get Total Daily Energy Expenditure (TDEE)
        3. Adjust based on fitness goals
        
        Note: We use default values for age and gender since those fields
        aren't in our current model. In a real app, you'd want to collect
        this info for more accurate calculations.
        """
        # Base metabolic rate (simplified Harris-Benedict equation)
        # Using average values for calculation since gender field is not available
        age = 30  # Default age if not specified
        if hasattr(self, 'age') and self.age:
            age = self.age
            
        if hasattr(self, 'gender') and self.gender == 'male':
            bmr = 88.362 + (13.397 * self.weight) + (4.799 * self.height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * self.weight) + (3.098 * self.height) - (4.330 * age)
        
        # Activity multiplier - how much more energy they burn than at rest
        activity_multipliers = {
            'sedentary': 1.2,      # Desk job, little exercise
            'light': 1.375,        # Exercise 1-3 days/week
            'moderate': 1.55,      # Exercise 3-5 days/week
            'active': 1.725,       # Exercise 6-7 days/week
            'very_active': 1.9     # Physical job or training twice/day
        }
        
        tdee = bmr * activity_multipliers.get(self.activity_level, 1.55)
        
        # Adjust based on goals
        if self.fitness_goal == 'weight_loss':
            return int(tdee - 500)  # 500 calorie deficit for sustainable weight loss
        elif self.fitness_goal == 'muscle_gain':
            return int(tdee + 300)  # 300 calorie surplus for muscle building
        else:
            return int(tdee)  # Maintenance - eat what you burn


class AIChatHistory(models.Model):
    """
    Records conversations between users and our AI fitness assistant.
    
    Every time a user asks a question, we save:
    - What they asked
    - How our AI responded
    - What the AI thought they wanted (intent detection)
    - How confident the AI was in its answer
    
    This helps us:
    1. Understand what users are asking about
    2. Improve our AI responses over time
    3. Spot patterns in user questions
    4. Train better models in the future
    
    Users can also mark responses as helpful or not,
    which gives us direct feedback on AI performance.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_chats'
    )
    
    # Message data
    user_message = models.TextField()
    ai_response = models.TextField()
    
    # AI metadata
    intent_detected = models.CharField(
        max_length=50,
        help_text="AI-detected intent of user message"
    )
    
    confidence_score = models.FloatField(
        default=0.0,
        help_text="AI confidence in response accuracy (0-1)"
    )
    
    ai_provider_used = models.CharField(
        max_length=50,
        default='rule-based',
        help_text="Which AI provider was used for this response"
    )
    
    # User feedback
    helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="Was the response helpful?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_chat_history'
        verbose_name = 'AI Chat History'
        verbose_name_plural = 'AI Chat Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ProgressTracking(models.Model):
    """
    Tracks overall user progress and provides AI-powered insights.
    
    This model captures comprehensive progress data that spans
    both workout and nutrition domains. It serves as the central
    repository for AI analysis and recommendations.
    
    The AI insights field contains natural language recommendations
    based on the user's actual progress and patterns across all
    aspects of their fitness journey.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress_tracking'
    )
    
    # Measurements
    weight = models.FloatField(null=True, blank=True)
    body_fat_percentage = models.FloatField(null=True, blank=True)
    muscle_mass = models.FloatField(null=True, blank=True)
    
    # Performance metrics
    workout_streak = models.IntegerField(default=0)
    total_workouts = models.IntegerField(default=0)
    calories_burned = models.IntegerField(default=0)
    
    # Nutrition metrics
    nutrition_adherence = models.FloatField(
        default=0.0,
        help_text="How well user follows nutrition plans (0-100)"
    )
    
    # AI insights
    progress_score = models.FloatField(
        default=0.0,
        help_text="AI-calculated overall progress score (0-100)"
    )
    
    achievement_badges = models.JSONField(
        default=list,
        help_text="List of earned achievement badges"
    )
    
    # AI recommendations
    ai_insights = models.TextField(
        blank=True,
        help_text="AI-generated insights and recommendations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_progress_tracking'
        verbose_name = 'Progress Tracking'
        verbose_name_plural = 'Progress Tracking'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Progress - {self.created_at.strftime('%Y-%m-%d')}"
