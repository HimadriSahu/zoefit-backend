"""
User serializers for ZoeFit comprehensive user data
"""

from rest_framework import serializers
from .models import UserProfile, UserActivity


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for user profile information.
    """
    full_name = serializers.ReadOnlyField()
    bmi = serializers.ReadOnlyField()
    weight_difference = serializers.ReadOnlyField()
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'user',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone_number',
            'date_of_birth',
            'profile_picture',
            'height',
            'weight',
            'target_weight',
            'fitness_goal',
            'activity_level',
            'workout_duration',
            'workout_types',
            'difficulty_level',
            'workout_type_preference',
            'dietary_preferences',
            'allergies',
            'medical_conditions',
            'gender',
            'breakfast_time',
            'lunch_time',
            'dinner_time',
            'body_fat_percentage',
            'muscle_mass',
            'bio',
            'location',
            'onboarding_completed',
            'onboarding_completed_at',
            'bmi',
            'weight_difference',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'onboarding_completed_at')
    
    def validate_height(self, value):
        """Validate height is within reasonable range (50-300 cm)."""
        if value and (value < 50 or value > 300):
            raise serializers.ValidationError("Height must be between 50 and 300 cm.")
        return value
    
    def validate_weight(self, value):
        """Validate weight is within reasonable range (20-500 kg)."""
        if value and (value < 20 or value > 500):
            raise serializers.ValidationError("Weight must be between 20 and 500 kg.")
        return value
    
    def validate_target_weight(self, value):
        """Validate target weight is within reasonable range."""
        if value and (value < 20 or value > 500):
            raise serializers.ValidationError("Target weight must be between 20 and 500 kg.")
        return value
    
    def validate_workout_duration(self, value):
        """Validate workout duration is reasonable (5-300 minutes)."""
        if value and (value < 5 or value > 300):
            raise serializers.ValidationError("Workout duration must be between 5 and 300 minutes.")
        return value
    
    def validate_body_fat_percentage(self, value):
        """Validate body fat percentage is reasonable (1-70%)."""
        if value and (value < 1 or value > 70):
            raise serializers.ValidationError("Body fat percentage must be between 1 and 70%.")
        return value


class UserProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating user profile (all fields optional except user).
    """
    class Meta:
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'profile_picture',
            'height',
            'weight',
            'target_weight',
            'fitness_goal',
            'activity_level',
            'workout_duration',
            'workout_types',
            'difficulty_level',
            'workout_type_preference',
            'dietary_preferences',
            'allergies',
            'medical_conditions',
            'gender',
            'breakfast_time',
            'lunch_time',
            'dinner_time',
            'body_fat_percentage',
            'muscle_mass',
            'bio',
            'location'
        )
    
    def validate_height(self, value):
        """Validate height is within reasonable range (50-300 cm)."""
        if value and (value < 50 or value > 300):
            raise serializers.ValidationError("Height must be between 50 and 300 cm.")
        return value
    
    def validate_weight(self, value):
        """Validate weight is within reasonable range (20-500 kg)."""
        if value and (value < 20 or value > 500):
            raise serializers.ValidationError("Weight must be between 20 and 500 kg.")
        return value
    
    def validate_target_weight(self, value):
        """Validate target weight is within reasonable range."""
        if value and (value < 20 or value > 500):
            raise serializers.ValidationError("Target weight must be between 20 and 500 kg.")
        return value
    
    def validate_workout_duration(self, value):
        """Validate workout duration is reasonable (5-300 minutes)."""
        if value and (value < 5 or value > 300):
            raise serializers.ValidationError("Workout duration must be between 5 and 300 minutes.")
        return value
    
    def validate_body_fat_percentage(self, value):
        """Validate body fat percentage is reasonable (1-70%)."""
        if value and (value < 1 or value > 70):
            raise serializers.ValidationError("Body fat percentage must be between 1 and 70%.")
        return value


class OnboardingSerializer(serializers.ModelSerializer):
    """
    Serializer for onboarding data submission.
    """
    class Meta:
        model = UserProfile
        fields = (
            'gender',
            'date_of_birth',
            'height',
            'weight',
            'target_weight',
            'fitness_goal',
            'activity_level',
            'breakfast_time',
            'lunch_time',
            'dinner_time',
            'phone_number',
            'bio',
            'location',
            'dietary_preferences',
            'allergies',
            'medical_conditions',
            'difficulty_level',
            'workout_type_preference',
            'workout_types',
            'body_fat_percentage',
            'muscle_mass',
        )
    
    def validate_height(self, value):
        """Validate height is within reasonable range (50-300 cm)."""
        if value and (value < 50 or value > 300):
            raise serializers.ValidationError("Height must be between 50 and 300 cm.")
        return value
    
    def validate_weight(self, value):
        """Validate weight is within reasonable range (20-500 kg)."""
        if value and (value < 20 or value > 500):
            raise serializers.ValidationError("Weight must be between 20 and 500 kg.")
        return value
    
    def validate_target_weight(self, value):
        """Validate target weight is within reasonable range."""
        if value and (value < 20 or value > 500):
            raise serializers.ValidationError("Target weight must be between 20 and 500 kg.")
        return value
    
    def validate_body_fat_percentage(self, value):
        """Validate body fat percentage is reasonable (1-70%)."""
        if value and (value < 1 or value > 70):
            raise serializers.ValidationError("Body fat percentage must be between 1 and 70%.")
        return value


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity tracking."""
    class Meta:
        model = UserActivity
        fields = (
            'id',
            'activity_type',
            'activity_data',
            'timestamp'
        )
        read_only_fields = ('id', 'timestamp')
