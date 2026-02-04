"""
Authentication Module - API Views

This module contains all API views for user authentication and profile management.
Endpoints include:
- User registration
- User login/logout
- Token refresh
- Profile management
- Password change

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
    UserProfileSerializer
)

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request):
    """
    API root endpoint - lists all available authentication endpoints.
    
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
            'profile': {
                'url': '/api/auth/profile/',
                'method': 'GET',
                'description': 'Get user profile',
                'authentication': 'Required'
            },
            'update_profile': {
                'url': '/api/auth/profile/update/',
                'method': 'PUT/PATCH',
                'description': 'Update user profile',
                'authentication': 'Required'
            },
            'forgot_password': {
                'url': '/api/auth/forgot-password/',
                'method': 'POST',
                'description': 'Request password reset email',
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
    User registration endpoint.
    
    POST /api/auth/register/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    User login endpoint.
    
    POST /api/auth/login/
    """
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current user profile.
    
    GET /api/auth/profile/
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user profile.
    
    PUT/PATCH /api/auth/profile/update/
    """
    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint (blacklist refresh token).
    
    POST /api/auth/logout/
    Body: {"refresh_token": "your_refresh_token"}
    """
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return Response({
            'error': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({
            'error': 'Invalid token',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Catch any other unexpected errors
        return Response({
            'error': 'An error occurred during logout',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Forgot password endpoint - sends reset email.
    
    POST /api/auth/forgot-password/
    Body: {
        "email": "user_email"
    }
    """
    email = request.data.get('email')
    
    if not email:
        return Response({
            'error': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email)
        
        # For now, just return success message
        # In production, you would send an email with reset link
        return Response({
            'message': 'Password reset instructions have been sent to your email address',
            'note': 'This is a demo - in production, an actual reset email would be sent'
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({
            'error': 'No account found with this email address'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': 'An error occurred',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change user password endpoint.
    
    POST /api/auth/change-password/
    Body: {
        "old_password": "current_password",
        "new_password": "new_password",
        "new_password2": "new_password"
    }
    """
    user = request.user
    
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    new_password2 = request.data.get('new_password2')
    
    if not old_password or not new_password or not new_password2:
        return Response({
            'error': 'All password fields are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if new_password != new_password2:
        return Response({
            'error': 'New passwords do not match'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.check_password(old_password):
        return Response({
            'error': 'Current password is incorrect'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate new password
    try:
        validate_password(new_password, user)
    except Exception as e:
        return Response({
            'error': 'Password validation failed',
            'details': list(e.messages) if hasattr(e, 'messages') else [str(e)]
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.set_password(new_password)
    user.save()
    
    return Response({
        'message': 'Password changed successfully'
    }, status=status.HTTP_200_OK)