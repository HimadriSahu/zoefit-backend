"""
URL patterns for user profile management

This file defines all the endpoints for managing user profiles:
- Viewing your current profile
- Creating a new profile
- Updating profile information
- Deleting your profile

Profile management is separate from authentication - users can exist
without profiles, but profiles provide a personalized experience
with photos, bios, and fitness preferences.

All endpoints require authentication since profile data is private
to each user and shouldn't be accessible to others.
"""

from django.urls import path
from .views import (
    profile_view,
    create_profile_view,
    update_profile_view,
    delete_profile_view
)

app_name = 'profiles'

urlpatterns = [
    # Profile Viewing and Management
    path('profile/', profile_view, name='profile'),
    
    # Profile Creation
    path('profile/create/', create_profile_view, name='create_profile'),
    
    # Profile Updates
    path('profile/update/', update_profile_view, name='update_profile'),
    
    # Profile Deletion
    path('profile/delete/', delete_profile_view, name='delete_profile'),
]
