"""
Workout module models for ZoeFit

This module contains all workout-related data models:
- Workout plans and exercises
- Workout preferences and equipment
- Workout sessions and completion tracking
- Workout progress and performance analytics

These models are specifically focused on workout functionality
and are separated from nutrition to create a more modular structure.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class WorkoutPlan(models.Model):
    """
    Personalized workout plans created by AI.
    
    Each workout plan is designed for a specific day in a user's
    fitness program. The AI considers:
    - User's current fitness level and goals
    - Equipment they have available
    - Previous workout performance
    - How they're progressing over time
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )
    
    day = models.IntegerField(
        help_text="Day number in the workout program"
    )
    
    # Workout data
    exercises = models.JSONField(
        help_text="List of exercises with sets, reps, and rest periods"
    )
    
    workout_type = models.CharField(
        max_length=50,
        choices=[
            ('strength', 'Strength Training'),
            ('cardio', 'Cardio'),
            ('hiit', 'HIIT'),
            ('flexibility', 'Flexibility'),
            ('mixed', 'Mixed Workout'),
        ],
        default='mixed'
    )
    
    # Duration and intensity
    estimated_duration = models.IntegerField(
        help_text="Estimated workout duration in minutes"
    )
    
    # Equipment requirements
    equipment_needed = models.JSONField(
        default=list,
        help_text="List of equipment needed for this workout"
    )
    
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    
    intensity_score = models.FloatField(
        default=5.0,
        help_text="Workout intensity score (1-10)"
    )
    
    # AI metadata
    generated_by_ai = models.BooleanField(default=True)
    adaptation_score = models.FloatField(
        default=0.0,
        help_text="How well this workout adapts to user's progress"
    )
    
    # User completion data
    completed = models.BooleanField(default=False)
    completion_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Actual time taken to complete workout"
    )
    
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="User workout rating 1-5"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_plans'
        verbose_name = 'Workout Plan'
        verbose_name_plural = 'Workout Plans'
        unique_together = ['user', 'day']
        ordering = ['day']
    
    def __str__(self):
        return f"{self.user.username}'s Workout - Day {self.day}"




class WorkoutSession(models.Model):
    """
    Tracks individual workout sessions for detailed analytics.
    
    This model captures the actual execution of workout plans,
    including timing, completion status, and user feedback.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_workout_sessions'
    )
    
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='sessions',
        null=True,
        blank=True,
        help_text="Associated workout plan if applicable"
    )
    
    # Session timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(
        null=True,
        blank=True
    )
    duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Actual workout duration"
    )
    
    # Session data
    exercises_completed = models.JSONField(
        default=list,
        help_text="List of exercises actually completed"
    )
    
    workout_type = models.CharField(
        max_length=50,
        choices=[
            ('strength', 'Strength Training'),
            ('cardio', 'Cardio'),
            ('hiit', 'HIIT'),
            ('flexibility', 'Flexibility'),
            ('mixed', 'Mixed Workout'),
        ],
        default='mixed'
    )
    
    # Performance metrics
    completed = models.BooleanField(default=False)
    calories_burned = models.IntegerField(
        default=0,
        help_text="Estimated calories burned"
    )
    
    # User feedback
    difficulty_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="User perceived difficulty 1-5"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="User notes about the workout session"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_sessions'
        verbose_name = 'Workout Session'
        verbose_name_plural = 'Workout Sessions'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username}'s Session - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class WorkoutProgress(models.Model):
    """
    Tracks workout-specific progress and performance metrics.
    
    This model focuses on workout performance trends,
    strength gains, endurance improvements, and consistency.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_progress'
    )
    
    # Performance metrics
    total_workouts = models.IntegerField(default=0)
    workout_streak = models.IntegerField(default=0)
    total_workout_time = models.DurationField(
        default='00:00:00',
        help_text="Total time spent working out"
    )
    total_calories_burned = models.IntegerField(default=0)
    
    # Strength metrics
    max_bench_press = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum bench press weight in kg"
    )
    max_squat = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum squat weight in kg"
    )
    max_deadlift = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum deadlift weight in kg"
    )
    
    # Cardio metrics
    max_run_distance = models.FloatField(
        null=True,
        blank=True,
        help_text="Maximum running distance in km"
    )
    best_5k_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Best 5K run time"
    )
    
    # AI insights
    performance_score = models.FloatField(
        default=0.0,
        help_text="AI-calculated performance score (0-100)"
    )
    
    achievement_badges = models.JSONField(
        default=list,
        help_text="List of workout-related achievement badges"
    )
    
    ai_insights = models.TextField(
        blank=True,
        help_text="AI-generated workout insights and recommendations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_progress'
        verbose_name = 'Workout Progress'
        verbose_name_plural = 'Workout Progress'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Workout Progress - {self.created_at.strftime('%Y-%m-%d')}"
