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
    Custom user model that uses email instead of username for login.
    
    Most people remember their email better than a username, so we made
    email the primary identifier. Username is still kept for display purposes
    since some users prefer having a public handle.
    
    Note: All fitness-related user data (height, weight, goals, etc.)
    should go in the UserProfile model, not here.
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        # Show username in admin interface, fallback to email if username is empty
        return self.username or self.email
