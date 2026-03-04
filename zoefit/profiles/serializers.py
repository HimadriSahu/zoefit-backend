"""
Profile serializers for ZoeFit user data

Serializers are the bridge between our database models and JSON responses.
They handle converting complex Python objects into simple JSON that the frontend can use,
and they validate incoming data to make sure it's safe and correct.

We have two serializers:
1. UserProfileSerializer - for reading/updating existing profiles
2. UserProfileCreateSerializer - for creating new profiles

The create serializer is slightly different because it doesn't include
read-only fields like ID and timestamps that are set automatically.
"""

from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.

    Handles reading and updating user profile data.
    
    This serializer includes all the profile fields plus the computed
    'full_name' property that combines first and last name.
    
    Some fields are read-only because they're managed automatically:
    - id: database primary key
    - created_at/updated_at: timestamps
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'date_of_birth',
            'profile_picture',
            'height',
            'weight',
            'fitness_goal',
            'bio',
            'location',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating user profile (all fields optional except user).
    
    Handles creating new user profiles.
    
    This serializer only includes fields that users can actually set
    when creating their profile. We exclude auto-generated fields
    like ID and timestamps since Django handles those automatically.
    
    All fields are optional because we want users to feel comfortable
    sharing only what they're ready to share.
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
            'fitness_goal',
            'bio',
            'location'
        )
