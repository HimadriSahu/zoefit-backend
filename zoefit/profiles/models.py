"""
User profile management for ZoeFit

This module handles the personal side of user accounts.
While the authentication module manages login/security,
the profiles module stores the personal details that make each user unique.

We keep profile data separate from authentication data for two reasons:
1. Security - personal info isn't needed for login
2. Flexibility - users can have rich profiles without bloating the auth system

The UserProfile model stores things like:
- Name and contact info
- Profile pictures and bios
- Fitness goals and measurements
- Location and preferences

This data helps us personalize the ZoeFit experience and make
our AI recommendations more accurate.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserProfile(models.Model):
    """
    Extended profile information for ZoeFit users.
    
    Every user has an authentication account (email, password, etc.)
    but not everyone has a profile right away. Users can create
    their profile when they're ready to personalize their experience.
    
    The profile is where we store the human side of things:
    - What's your name and how do you look?
    - What are your fitness goals?
    - Where are you located?
    - Tell us about yourself in your bio
    
    All fields are optional because we want users to feel comfortable
    sharing only what they're comfortable with.
    
    Note: Some fitness data like height/weight might also be stored
    in the AI HealthMetrics model. We keep both because:
    - Profile data is for user display and preferences
    - HealthMetrics data is for AI calculations
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Personal Information
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Fitness Information
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
    fitness_goal = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('weight_loss', 'Weight Loss'),
            ('muscle_gain', 'Muscle Gain'),
            ('maintenance', 'Maintenance'),
            ('endurance', 'Endurance'),
        ]
    )
    
    # Additional fields
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
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
        """
        Get the user's full name for display purposes.
        
        Falls back to username if first/last name aren't set.
        This ensures we always have something to display.
        """
        return f"{self.first_name} {self.last_name}".strip() or self.user.username
