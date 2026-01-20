"""
Authentication Module - User Model

This module contains the custom User model for the ZoeFit application.
The User model extends Django's AbstractUser to include fitness-related fields.

This is part of the authentication module which handles:
- User registration and authentication
- JWT token management
- User profile management
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    This allows us to add custom fields in the future if needed.
    """
    email = models.EmailField(unique=True,)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for fitness app
    height = models.FloatField(blank=True, null=True, help_text="Height in cm")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kg")
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
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        # verbose_name = 'User'
        # verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
