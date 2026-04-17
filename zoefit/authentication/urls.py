"""
URL patterns for user authentication

This file defines all the endpoints for user account management:
- Registration and login
- Token management (JWT)
- Password reset and changes
- Logout functionality

Each path maps to a specific view function that handles the request.
The URLs are organized logically to make the API easy to understand.

We use JWT tokens instead of sessions for better scalability
and support for mobile/single-page applications.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    api_root_view,
    register_view,
    login_view,
    logout_view,
    forgot_password_view,
    reset_password_view,
    change_password_view
)

app_name = 'authentication'

urlpatterns = [
    # API Documentation and Discovery
    path('', api_root_view, name='api_root'),
    
    # User Account Management
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Password Management
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/', reset_password_view, name='reset_password'),
    path('change-password/', change_password_view, name='change_password'),
    
    # Token Management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

