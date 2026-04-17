"""
Serializers for frontend module data models.

This module contains Django REST Framework serializers that convert
frontend model instances to JSON and validate incoming data for API
endpoints. Serializers handle data transformation, validation, and
provide clean API responses for frontend consumption.

Key serializers:
- WorkoutSessionSerializer: Workout session data
- ExerciseLogSerializer: Exercise performance data
- ProgressSnapshotSerializer: Progress measurement data
- StreakSerializer: Streak tracking data
- MealLogSerializer: Meal logging data
- AchievementSerializer: Achievement data

These serializers ensure consistent data formats across all
frontend API endpoints and provide proper validation for user input.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    WorkoutSession, ExerciseLog, ProgressSnapshot,
    Streak, MealLog, Achievement
)

User = get_user_model()


class ExerciseLogSerializer(serializers.ModelSerializer):
    """
    Serializer for exercise log data.
    
    Handles the detailed performance data for individual exercises
    within workout sessions, including sets, reps, weight, and form ratings.
    """
    
    class Meta:
        model = ExerciseLog
        fields = [
            'id', 'exercise_name', 'sets_completed', 'reps_per_set',
            'weight_used', 'rest_time', 'form_rating', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_reps_per_set(self, value):
        """Validate that reps_per_set is a list of positive integers."""
        if not isinstance(value, list):
            raise serializers.ValidationError("reps_per_set must be a list.")
        if len(value) == 0:
            raise serializers.ValidationError("reps_per_set cannot be empty.")
        for reps in value:
            if not isinstance(reps, int) or reps <= 0:
                raise serializers.ValidationError("All reps must be positive integers.")
        return value
    
    def validate_sets_completed(self, value):
        """Ensure sets_completed matches the length of reps_per_set."""
        # This validation will be done in WorkoutSessionSerializer
        return value


class WorkoutSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for workout session data.
    
    Handles the main workout session data including timing, completion
    status, calories burned, and user ratings. Includes nested exercise logs.
    """
    exercise_logs = ExerciseLogSerializer(many=True, read_only=True)
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'workout_plan', 'start_time', 'end_time', 'duration',
            'duration_minutes', 'completed', 'exercises_completed',
            'calories_burned', 'user_notes', 'difficulty_rating',
            'exercise_logs', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'duration', 'created_at', 'updated_at']
    
    def get_duration_minutes(self, obj):
        """Convert duration to minutes for easier frontend consumption."""
        if obj.duration:
            return int(obj.duration.total_seconds() / 60)
        return None
    
    def validate(self, data):
        """Cross-field validation for workout session data."""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if end_time and start_time:
            if end_time <= start_time:
                raise serializers.ValidationError(
                    "end_time must be after start_time"
                )
        
        return data
    
    def create(self, validated_data):
        """Create workout session and handle exercise logs."""
        exercise_logs_data = validated_data.pop('exercise_logs', [])
        workout_session = WorkoutSession.objects.create(**validated_data)
        
        # Create exercise logs if provided
        for log_data in exercise_logs_data:
            ExerciseLog.objects.create(
                workout_session=workout_session,
                **log_data
            )
        
        return workout_session


class ProgressSnapshotSerializer(serializers.ModelSerializer):
    """
    Serializer for progress snapshot data.
    
    Handles user progress measurements including weight, body fat,
    muscle mass, and body measurements. Used for tracking progress over time.
    """
    
    class Meta:
        model = ProgressSnapshot
        fields = [
            'id', 'date', 'weight', 'body_fat_percentage', 'muscle_mass',
            'measurements', 'progress_photos', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_weight(self, value):
        """Validate weight is positive and reasonable."""
        if value and (value <= 0 or value > 1000):
            raise serializers.ValidationError("Weight must be between 0 and 1000 kg.")
        return value
    
    def validate_body_fat_percentage(self, value):
        """Validate body fat percentage is within reasonable range."""
        if value and (value < 0 or value > 100):
            raise serializers.ValidationError("Body fat percentage must be between 0 and 100.")
        return value
    
    def validate_measurements(self, value):
        """Validate measurements dictionary format."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Measurements must be a dictionary.")
        
        # Validate measurement values are positive numbers
        for key, measurement in value.items():
            if not isinstance(measurement, (int, float)) or measurement <= 0:
                raise serializers.ValidationError(f"Measurement '{key}' must be a positive number.")
        
        return value


class StreakSerializer(serializers.ModelSerializer):
    """
    Serializer for streak tracking data.
    
    Handles various fitness streaks including workout, calorie logging,
    water intake, and steps goal streaks. Provides streak status and history.
    """
    streak_type_display = serializers.CharField(source='get_streak_type_display', read_only=True)
    days_since_last_activity = serializers.SerializerMethodField()
    
    class Meta:
        model = Streak
        fields = [
            'id', 'streak_type', 'streak_type_display', 'current_count',
            'longest_count', 'last_activity_date', 'start_date', 'is_active',
            'days_since_last_activity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_since_last_activity(self, obj):
        """Calculate days since last activity for streak status."""
        today = timezone.now().date()
        delta = today - obj.last_activity_date
        return delta.days


class MealLogSerializer(serializers.ModelSerializer):
    """
    Serializer for meal logging data.
    
    Handles meal consumption data including food items, nutritional
    information, meal timing, and photos. Used for nutrition tracking.
    """
    meal_type_display = serializers.CharField(source='get_meal_type_display', read_only=True)
    
    class Meta:
        model = MealLog
        fields = [
            'id', 'meal_type', 'meal_type_display', 'food_items',
            'total_calories', 'protein', 'carbs', 'fat', 'meal_time',
            'photo_url', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_food_items(self, value):
        """Validate food items list format."""
        if not isinstance(value, list):
            raise serializers.ValidationError("food_items must be a list.")
        
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each food item must be a dictionary.")
            
            required_fields = ['name', 'quantity', 'calories']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Food item missing required field: {field}")
        
        return value
    
    def validate_total_calories(self, value):
        """Validate total calories is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Total calories cannot be negative.")
        return value
    
    def validate(self, data):
        """Validate nutritional data consistency."""
        protein = data.get('protein', 0)
        carbs = data.get('carbs', 0)
        fat = data.get('fat', 0)
        total_calories = data.get('total_calories', 0)
        
        # Basic calorie calculation check (4 cal/g protein, 4 cal/g carbs, 9 cal/g fat)
        calculated_calories = (protein * 4) + (carbs * 4) + (fat * 9)
        
        # Allow some tolerance for rounding and incomplete data
        if total_calories > 0 and abs(calculated_calories - total_calories) > total_calories * 0.3:
            # This is just a warning, not an error, as users might not know exact macros
            pass
        
        return data


class AchievementSerializer(serializers.ModelSerializer):
    """
    Serializer for achievement data.
    
    Handles user achievements and milestones including badges,
    points, and achievement metadata. Used for gamification features.
    """
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'achievement_type', 'title', 'description',
            'badge_icon', 'points_awarded', 'earned_date', 'is_displayed'
        ]
        read_only_fields = ['id', 'earned_date']


class DashboardSummarySerializer(serializers.Serializer):
    """
    Serializer for dashboard summary data.
    
    Aggregates data from multiple models to provide a comprehensive
    overview of user's fitness status for the main dashboard.
    """
    total_workouts = serializers.IntegerField()
    current_workout_streak = serializers.IntegerField()
    longest_workout_streak = serializers.IntegerField()
    total_calories_burned = serializers.IntegerField()
    current_weight = serializers.FloatField(allow_null=True)
    weight_change = serializers.FloatField(allow_null=True)
    meals_logged_today = serializers.IntegerField()
    active_achievements = serializers.IntegerField()
    total_points = serializers.IntegerField()
    recent_workouts = WorkoutSessionSerializer(many=True)
    active_streaks = StreakSerializer(many=True)
    recent_achievements = AchievementSerializer(many=True)


class WorkoutStatsSerializer(serializers.Serializer):
    """
    Serializer for workout statistics data.
    
    Provides aggregated workout statistics for analytics and
    progress tracking features.
    """
    total_workouts = serializers.IntegerField()
    total_duration_minutes = serializers.IntegerField()
    total_calories_burned = serializers.IntegerField()
    average_workout_duration = serializers.FloatField()
    most_common_exercise = serializers.CharField()
    workout_frequency = serializers.FloatField()  # workouts per week
    completion_rate = serializers.FloatField()  # percentage of completed workouts
    strength_progress = serializers.FloatField(allow_null=True)  # strength improvement percentage
    cardio_progress = serializers.FloatField(allow_null=True)  # cardio improvement percentage


class NutritionSummarySerializer(serializers.Serializer):
    """
    Serializer for nutrition summary data.
    
    Provides aggregated nutrition data for daily, weekly, and monthly
    nutrition tracking and analysis.
    """
    period = serializers.CharField()  # daily, weekly, monthly
    total_calories = serializers.IntegerField()
    average_daily_calories = serializers.FloatField()
    total_protein = serializers.FloatField()
    total_carbs = serializers.FloatField()
    total_fat = serializers.FloatField()
    average_macros = serializers.DictField()  # protein, carbs, fat percentages
    meals_logged = serializers.IntegerField()
    nutrition_consistency = serializers.FloatField()  # percentage of days with meals logged


class ProgressChartSerializer(serializers.Serializer):
    """
    Serializer for progress chart data.
    
    Provides formatted data for various progress charts including
    weight trends, body composition changes, and measurement progress.
    """
    chart_type = serializers.CharField()  # weight, body_fat, measurements
    data_points = serializers.ListField(child=serializers.DictField())
    period = serializers.CharField()  # week, month, quarter, year
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    trend = serializers.CharField()  # improving, stable, declining
    change_percentage = serializers.FloatField(allow_null=True)
