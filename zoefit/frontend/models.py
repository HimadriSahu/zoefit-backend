"""
Frontend data models for ZoeFit

This module contains the data models that power the user-facing features
of ZoeFit. These models store the actual user activity data that complements
the AI-generated plans and recommendations.

Key features:
- WorkoutSession: Tracks actual workout completions
- ExerciseLog: Detailed exercise performance data
- ProgressSnapshot: Time-based progress measurements
- Streak: Various fitness streak tracking
- MealLog: User meal consumption tracking

These models are designed to work seamlessly with the AI features module,
providing the actual data that AI uses to improve recommendations and
track user progress toward their fitness goals.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class WorkoutSession(models.Model):
    """
    Tracks actual workout sessions completed by users.
    
    While the AI features module creates workout plans, this model
    captures what users actually do - their real workout sessions.
    This data is crucial for:
    - Progress tracking and analytics
    - AI learning and plan improvement
    - Streak calculations
    - Achievement unlocking
    
    Each session can be linked to a planned workout or be a custom workout.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='frontend_workout_sessions'
    )
    
    workout_plan = models.ForeignKey(
        'workout.WorkoutPlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actual_sessions',
        help_text="The AI-generated workout plan this session follows"
    )
    
    start_time = models.DateTimeField(
        help_text="When the workout session started"
    )
    
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the workout session ended"
    )
    
    duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Total duration of the workout session"
    )
    
    completed = models.BooleanField(
        default=False,
        help_text="Whether the workout was completed as planned"
    )
    
    exercises_completed = models.JSONField(
        default=list,
        help_text="List of exercises completed with their details"
    )
    
    calories_burned = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Estimated calories burned during the session"
    )
    
    user_notes = models.TextField(
        blank=True,
        help_text="User's notes about the workout session"
    )
    
    difficulty_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User's rating of workout difficulty (1-5)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'frontend_workout_sessions'
        verbose_name = 'Workout Session'
        verbose_name_plural = 'Workout Sessions'
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', '-start_time']),
            models.Index(fields=['user', 'completed']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Workout - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        """
        Auto-calculate duration when end_time is set.
        """
        if self.end_time and not self.duration:
            self.duration = self.end_time - self.start_time
        super().save(*args, **kwargs)


class ExerciseLog(models.Model):
    """
    Detailed logging of individual exercises within workout sessions.
    
    This model captures the granular performance data for each exercise
    performed during a workout session. This data is essential for:
    - Progressive overload tracking
    - Performance analytics
    - AI plan optimization
    - Form improvement recommendations
    
    Each log represents one exercise performed in one workout session.
    """
    workout_session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name='exercise_logs'
    )
    
    exercise_name = models.CharField(
        max_length=100,
        help_text="Name of the exercise performed"
    )
    
    sets_completed = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of sets completed"
    )
    
    reps_per_set = models.JSONField(
        help_text="List of reps completed for each set"
    )
    
    weight_used = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Weight used in kg"
    )
    
    rest_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Rest time between sets"
    )
    
    form_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User's rating of exercise form (1-5)"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notes about this specific exercise"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'frontend_exercise_logs'
        verbose_name = 'Exercise Log'
        verbose_name_plural = 'Exercise Logs'
        ordering = ['workout_session', 'id']
        indexes = [
            models.Index(fields=['workout_session', 'exercise_name']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.exercise_name} - {self.workout_session}"


class ProgressSnapshot(models.Model):
    """
    Time-based snapshots of user's physical progress.
    
    This model captures the user's physical measurements and progress
    at specific points in time. This data is crucial for:
    - Progress visualization and charts
    - Goal tracking and achievement
    - AI plan adjustments
    - Motivation and milestone celebrations
    
    Users can create snapshots manually or they can be auto-generated
    from workout and nutrition data.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress_snapshots'
    )
    
    date = models.DateField(
        help_text="Date of the progress snapshot"
    )
    
    weight = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Weight in kg"
    )
    
    body_fat_percentage = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Body fat percentage"
    )
    
    muscle_mass = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Muscle mass in kg"
    )
    
    measurements = models.JSONField(
        default=dict,
        help_text="Body measurements in cm (chest, waist, arms, thighs, etc.)"
    )
    
    progress_photos = models.JSONField(
        default=list,
        help_text="URLs to progress photos"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="User notes about this progress snapshot"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'frontend_progress_snapshots'
        verbose_name = 'Progress Snapshot'
        verbose_name_plural = 'Progress Snapshots'
        ordering = ['-date']
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Progress - {self.date}"


class Streak(models.Model):
    """
    Tracks various fitness streaks for motivation and consistency.
    
    Streaks are powerful motivators for fitness consistency. This model
    tracks different types of streaks to encourage users to maintain
    their fitness habits. Streak types include:
    - Workout streak: Consecutive days with workouts
    - Calorie logging: Consecutive days with food logged
    - Water intake: Consecutive days meeting water goals
    - Steps goal: Consecutive days meeting step targets
    
    The system automatically updates streaks based on user activity.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='streaks'
    )
    
    STREAK_TYPES = [
        ('workout', 'Workout Streak'),
        ('calorie', 'Calorie Logging Streak'),
        ('water', 'Water Intake Streak'),
        ('steps', 'Steps Goal Streak'),
        ('meal_plan', 'Meal Plan Adherence Streak'),
    ]
    
    streak_type = models.CharField(
        max_length=50,
        choices=STREAK_TYPES,
        help_text="Type of streak being tracked"
    )
    
    current_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current streak count"
    )
    
    longest_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Longest streak achieved"
    )
    
    last_activity_date = models.DateField(
        help_text="Date of last activity for this streak"
    )
    
    start_date = models.DateField(
        help_text="Date when the current streak started"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the streak is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'frontend_streaks'
        verbose_name = 'Streak'
        verbose_name_plural = 'Streaks'
        unique_together = ['user', 'streak_type']
        indexes = [
            models.Index(fields=['user', 'streak_type']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['-updated_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_streak_type_display()} - {self.current_count} days"


class MealLog(models.Model):
    """
    Tracks actual meals consumed by users.
    
    While the AI features module creates meal plans, this model captures
    what users actually eat. This data is essential for:
    - Nutrition tracking and analysis
    - Progress toward fitness goals
    - AI meal plan improvement
    - Dietary pattern analysis
    
    Users can log meals manually, scan barcodes, or take photos of meals.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meal_logs'
    )
    
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    meal_type = models.CharField(
        max_length=20,
        choices=MEAL_TYPES,
        help_text="Type of meal"
    )
    
    food_items = models.JSONField(
        default=list,
        help_text="List of food items with quantities and nutritional info"
    )
    
    total_calories = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Total calories in the meal"
    )
    
    protein = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Protein content in grams"
    )
    
    carbs = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Carbohydrate content in grams"
    )
    
    fat = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Fat content in grams"
    )
    
    meal_time = models.DateTimeField(
        default=timezone.now,
        help_text="When the meal was consumed"
    )
    
    photo_url = models.URLField(
        blank=True,
        help_text="URL to meal photo"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="User notes about the meal"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'frontend_meal_logs'
        verbose_name = 'Meal Log'
        verbose_name_plural = 'Meal Logs'
        ordering = ['-meal_time']
        indexes = [
            models.Index(fields=['user', '-meal_time']),
            models.Index(fields=['user', 'meal_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s {self.get_meal_type_display()} - {self.meal_time.strftime('%Y-%m-%d %H:%M')}"


class Achievement(models.Model):
    """
    Tracks user achievements and milestones.
    
    This model stores the various achievements users can unlock
    through their fitness journey. Achievements provide motivation
    and recognition for reaching important milestones.
    
    Achievements can be automatically awarded based on:
    - Streak milestones
    - Workout consistency
    - Progress achievements
    - Special challenges completed
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    
    achievement_type = models.CharField(
        max_length=50,
        help_text="Type of achievement"
    )
    
    title = models.CharField(
        max_length=100,
        help_text="Achievement title"
    )
    
    description = models.TextField(
        help_text="Achievement description"
    )
    
    badge_icon = models.CharField(
        max_length=50,
        help_text="Icon identifier for the achievement badge"
    )
    
    points_awarded = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Points awarded for this achievement"
    )
    
    earned_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the achievement was earned"
    )
    
    is_displayed = models.BooleanField(
        default=True,
        help_text="Whether to display this achievement on profile"
    )
    
    class Meta:
        db_table = 'frontend_achievements'
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'
        ordering = ['-earned_date']
        indexes = [
            models.Index(fields=['user', '-earned_date']),
            models.Index(fields=['achievement_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
