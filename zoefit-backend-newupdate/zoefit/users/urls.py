"""
URL patterns for user management

This file defines all the endpoints for managing user data:
- Profile viewing and updates
- Onboarding submission and status
- Profile picture management
- Activity tracking
- Analytics and insights

All endpoints match the frontend API service expectations.
"""

from django.urls import path
from .views import (
    profile_view,
    update_profile_view,
    onboarding_view,
    onboarding_status_view,
    upload_profile_picture_view,
    delete_profile_picture_view,
    profile_analytics_view,
    track_activity_view,
    activities_view,
    contact_info_view,
    update_contact_info_view
)

app_name = 'users'

urlpatterns = [
    # Profile Management
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update_profile'),
    
    # Contact Information Management
    path('contact/', contact_info_view, name='contact_info'),
    path('contact/update/', update_contact_info_view, name='update_contact_info'),
    
    # Profile Picture Management
    path('profile/picture/upload/', upload_profile_picture_view, name='upload_profile_picture'),
    path('profile/picture/delete/', delete_profile_picture_view, name='delete_profile_picture'),
    
    # Profile Analytics
    path('profile/analytics/', profile_analytics_view, name='profile_analytics'),
    
    # Onboarding
    path('onboarding/', onboarding_view, name='onboarding'),
    path('onboarding/status/', onboarding_status_view, name='onboarding_status'),
    
    # Activity Tracking
    path('activity/', track_activity_view, name='track_activity'),
    path('activities/', activities_view, name='activities'),
]
