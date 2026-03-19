"""
User management module for ZoeFit

This module handles comprehensive user data including:
- Personal information and profiles
- Health metrics and fitness goals
- Onboarding data and preferences
- Activity tracking and progress

The frontend expects all user-related endpoints under /api/users/
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfile(models.Model):
    """
    Comprehensive user profile for ZoeFit.
    
    This model stores all user-related data in one place to make
    data synchronization easier and more reliable.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_profile'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Health & Fitness Information
    height = models.FloatField(
        blank=True, 
        null=True, 
        help_text="Height in cm"
    )
    weight = models.FloatField(
        blank=True, 
        null=True, 
        help_text="Weight in kg"
    )
    target_weight = models.FloatField(
        blank=True, 
        null=True, 
        help_text="Target weight in kg"
    )
    fitness_goal = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('lose_weight', 'Lose Weight'),
            ('gain_muscle', 'Gain Muscle'),
            ('maintain', 'Maintain Weight'),
            ('eat_healthier', 'Eat Healthier'),
        ]
    )
    activity_level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('sedentary', 'Sedentary (little or no exercise)'),
            ('light', 'Light (1-3 days/week)'),
            ('moderate', 'Moderate (3-5 days/week)'),
            ('active', 'Active (6-7 days/week)'),
            ('very_active', 'Very Active (twice per day)'),
        ]
    )
    
    # Workout Preferences
    workout_duration = models.IntegerField(
        blank=True,
        null=True,
        help_text="Preferred workout duration in minutes"
    )
    workout_types = models.JSONField(
        blank=True,
        null=True,
        help_text="List of preferred workout types"
    )
    difficulty_level = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ]
    )
    workout_type_preference = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('strength', 'Strength'),
            ('cardio', 'Cardio'),
            ('hiit', 'HIIT'),
            ('flexibility', 'Flexibility'),
            ('mixed', 'Mixed'),
        ]
    )
    
    # Dietary Preferences
    dietary_preferences = models.JSONField(
        blank=True,
        null=True,
        help_text="List of dietary preferences"
    )
    allergies = models.JSONField(
        blank=True,
        null=True,
        help_text="List of food allergies"
    )
    medical_conditions = models.JSONField(
        blank=True,
        null=True,
        help_text="List of medical conditions"
    )
    
    # Onboarding Information
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ]
    )
    breakfast_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Preferred breakfast time"
    )
    lunch_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Preferred lunch time"
    )
    dinner_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Preferred dinner time"
    )
    
    # Body Composition
    body_fat_percentage = models.FloatField(
        blank=True,
        null=True,
        help_text="Body fat percentage"
    )
    muscle_mass = models.FloatField(
        blank=True,
        null=True,
        help_text="Muscle mass in kg"
    )
    
    # Additional fields
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Onboarding completion tracking
    onboarding_completed = models.BooleanField(default=False)
    onboarding_completed_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def full_name(self):
        """Get the user's full name for display purposes."""
        return f"{self.first_name} {self.last_name}".strip() or self.user.username
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight are available."""
        if self.height and self.weight:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return None
    
    @property
    def weight_difference(self):
        """Calculate the difference between current weight and target weight."""
        if self.weight and self.target_weight:
            return round(self.target_weight - self.weight, 2)
        return None
    
    def get_fitness_goal_display(self):
        """Get the human-readable display name for the fitness goal."""
        goal_choices = dict(self._meta.get_field('fitness_goal').choices)
        return goal_choices.get(self.fitness_goal, self.fitness_goal)
    
    def get_activity_level_display(self):
        """Get the human-readable display name for the activity level."""
        activity_choices = dict(self._meta.get_field('activity_level').choices)
        return activity_choices.get(self.activity_level, self.activity_level)


class UserActivity(models.Model):
    """Track user activities for analytics and progress tracking."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('workout_completed', 'Workout Completed'),
            ('meal_logged', 'Meal Logged'),
            ('goal_updated', 'Goal Updated'),
            ('weight_updated', 'Weight Updated'),
            ('profile_updated', 'Profile Updated'),
        ]
    )
    activity_data = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional data about the activity"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"
