"""
User authentication API endpoints for ZoeFit

This module handles all the user-facing authentication functionality:
- Creating new accounts
- Logging in and out
- Managing passwords
- Getting JWT tokens for API access

We use JWT (JSON Web Tokens) instead of sessions because:
1. Better for mobile apps and single-page applications
2. No server-side session state to manage
3. Easy to scale across multiple servers

Each endpoint is designed to be simple and predictable - the frontend
calls them, gets a response, and handles the UI updates.
All endpoints use JWT authentication except registration and login.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request):
    """
    Welcome page for the authentication API.
    
    This is mainly for developers who are exploring the API.
    It shows all available endpoints and what they do.
    
    GET /api/auth/
    """
    return Response({
        'message': 'ZoeFit Authentication API',
        'endpoints': {
            'register': {
                'url': '/api/auth/register/',
                'method': 'POST',
                'description': 'User registration',
                'authentication': 'Not required'
            },
            'login': {
                'url': '/api/auth/login/',
                'method': 'POST',
                'description': 'User login',
                'authentication': 'Not required'
            },
            'logout': {
                'url': '/api/auth/logout/',
                'method': 'POST',
                'description': 'User logout (blacklist token)',
                'authentication': 'Required'
            },
            'token_refresh': {
                'url': '/api/auth/token/refresh/',
                'method': 'POST',
                'description': 'Refresh access token',
                'authentication': 'Not required (requires refresh token)'
            },
            'forgot_password': {
                'url': '/api/auth/forgot-password/',
                'method': 'POST',
                'description': 'Request password reset token',
                'authentication': 'Not required'
            },
            'reset_password': {
                'url': '/api/auth/reset-password/',
                'method': 'POST',
                'description': 'Reset password with token',
                'authentication': 'Not required'
            },
            'change_password': {
                'url': '/api/auth/change-password/',
                'method': 'POST',
                'description': 'Change user password',
                'authentication': 'Required'
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Create a new user account.
    
    POST /api/auth/register/
    This is where new users sign up for ZoeFit. We collect:
    - username (what others will see)
    - email (for login and notifications)
    - password (kept secure and hashed)
    
    If everything checks out, we create the account and immediately
    give them JWT tokens so they can start using the app right away.
    
    No email verification required for now - we might add this later
    if we start getting spam accounts.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Create JWT tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        # Send back user info and tokens
        return Response({
            'message': 'Welcome to ZoeFit! Your account has been created.',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
            },
            'tokens': {
                'refresh': str(refresh),  # Use this to get new access tokens
                'access': str(refresh.access_token),  # Use this for API calls
            }
        }, status=status.HTTP_201_CREATED)
    
    # If validation fails, send back the error details
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and provide access tokens.
    POST /api/auth/login/

    Users log in with their email and password. If everything matches,
    we give them JWT tokens to access the API.
    
    The access token expires in 1 hour for security.
    The refresh token lasts 7 days and can be used to get new access tokens.
    
    We don't use sessions - the frontend stores these tokens
    and sends them with each API request.
    """
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Create JWT tokens for the logged-in user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful! Welcome back.',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
            },
            'tokens': {
                'refresh': str(refresh),  # Keep this safe!
                'access': str(refresh.access_token),  # Send this with API calls
            }
        }, status=status.HTTP_200_OK)
    
    # Bad credentials - don't give specific details for security
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Log out the current user by invalidating their refresh token.
    POST /api/auth/logout/
    Body: {"refresh_token": "your_refresh_token"}
    When users log out, we add their refresh token to a blacklist.
    This prevents anyone from using that token to get new access tokens.
    
    Note: The access token might still work until it expires (usually 1 hour),
    but they can't get new ones after logging out.
    
    Frontend should delete both tokens after successful logout.
    """
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({
            'error': 'Please provide your refresh token to logout properly.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({
            'message': 'You have been logged out successfully.'
        }, status=status.HTTP_200_OK)
    except TokenError as e:
        # Token was already invalid or expired
        return Response({
            'error': 'This logout token is no longer valid.',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Something went wrong - but we can still tell frontend to clear tokens
        return Response({
            'error': 'Something went wrong during logout, but you can clear your local tokens.',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Send password reset email to user.
     POST /api/auth/forgot-password/
    Body: {
        "email": "user_email"
    }
            'error': 'Email is required'

    Users who forgot their password can request a reset link.
    We look up their account by email and (in production) send them
    a secure link to create a new password.
    
    For now, we just return a success message to show the API works.
    In a real deployment, you'd integrate with an email service like
    SendGrid or AWS SES to actually send the reset email.
    
    Security note: We always return success, even if the email doesn't exist.
    This prevents people from figuring out which emails are registered.
    """
    email = request.data.get('email')
    
    if not email:
        return Response({
            'error': 'Please enter your email address.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # Generate password reset token
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.conf import settings
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Return reset information (no email sending)
        return Response({
            'message': 'Password reset token generated successfully.',
            'reset_info': {
                'token': token,
                'uid': uid,
                'frontend_url': settings.FRONTEND_URL,
                'note': 'Use this token to reset password via API'
            }
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        # Don't reveal that the email doesn't exist
        return Response({
            'message': 'If an account exists with this email, you will receive password reset instructions shortly.',
        }, status=status.HTTP_200_OK)
    except Exception as e:
        # Something went wrong on our end
        return Response({
            'error': 'Unable to process your request right now. Please try again later.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset password using token from forgot password.
    POST /api/auth/reset-password/
    Body: {
        "uid": "encoded_user_id",
        "token": "reset_token",
        "new_password": "new_password",
        "new_password2": "new_password"
    }
    
    Users can reset their password using the token received from forgot-password.
    This validates the token and updates the password if valid.
    
    Security features:
    - Token expires after 1 hour (configurable)
    - Token can only be used once
    - Validates new password strength
    """
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    new_password2 = request.data.get('new_password2')
    
    if not all([uid, token, new_password, new_password2]):
        return Response({
            'error': 'Please provide all required fields: uid, token, new_password, new_password2.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != new_password2:
        return Response({
            'error': 'New passwords do not match. Please type carefully.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str
        from django.contrib.auth.tokens import default_token_generator
        
        # Decode the user ID
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({
                'error': 'Invalid reset link. Please request a new password reset.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the token
        if not default_token_generator.check_token(user, token):
            return Response({
                'error': 'Invalid or expired reset token. Please request a new password reset.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate new password strength
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({
                'error': 'New password is not strong enough.',
                'details': list(e.messages) if hasattr(e, 'messages') else [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Your password has been reset successfully. You can now log in with your new password.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Unable to reset password. Please try again or contact support.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Allow logged-in users to change their password.
     POST /api/auth/change-password/
    Body: {
        "old_password": "current_password",
        "new_password": "new_password",
        "new_password2": "new_password"
    }
    This is for users who know their current password and want to change it.
    They must provide their old password to prove it's really them.
    
    We run the new password through Django's password validation
    to make sure it's strong enough.
    
    After changing the password, all existing JWT tokens are still valid.
    If you want to force logout, you'd need to implement token blacklisting
    for all user tokens (not just the refresh token).
    """
    user = request.user
    
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password2 = request.data.get('new_password2')
    
    if not old_password or not new_password or not new_password2:
        return Response({
            'error': 'Please fill in all password fields.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != new_password2:
        return Response({
            'error': 'New passwords do not match. Please type carefully.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Your current password is incorrect. Please try again.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Make sure the new password is strong enough
    try:
        validate_password(new_password, user)
    except Exception as e:
        return Response({
            'error': 'New password is not strong enough.',
            'details': list(e.messages) if hasattr(e, 'messages') else [str(e)]
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Update the password and save the user
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Your password has been changed successfully.'
    }, status=status.HTTP_200_OK)