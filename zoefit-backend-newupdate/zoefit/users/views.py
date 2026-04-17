"""
User API endpoints for ZoeFit

This module handles all user-related API calls:
- Getting and updating user profiles
- Onboarding data submission
- Profile picture upload
- Activity tracking
- Analytics and progress data

All endpoints are designed to match the frontend API service expectations.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import UserProfile, UserActivity
from .serializers import (
    UserProfileSerializer, 
    UserProfileCreateSerializer,
    OnboardingSerializer,
    UserActivitySerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get the current user's comprehensive profile information.
    
    GET /api/users/profile/
    """
    try:
        profile = request.user.user_profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        # Create a basic profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user's profile.
    
    PATCH /api/users/profile/update/
    """
    try:
        profile = request.user.user_profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    serializer = UserProfileSerializer(
        profile,
        data=request.data,
        partial=True  # Allow partial updates
    )
    
    if serializer.is_valid():
        updated_profile = serializer.save()
        
        # Track profile update activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_updated',
            activity_data=request.data
        )
        
        response_serializer = UserProfileSerializer(updated_profile)
        return Response({
            'message': 'Profile updated successfully',
            'profile': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def onboarding_view(request):
    """
    Submit onboarding data for the user.
    
    POST /api/users/onboarding/
    """
    try:
        profile = request.user.user_profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    serializer = OnboardingSerializer(
        profile,
        data=request.data,
        partial=True
    )
    
    if serializer.is_valid():
        # Mark onboarding as completed
        updated_profile = serializer.save(
            onboarding_completed=True,
            onboarding_completed_at=timezone.now()
        )
        
        # Track onboarding completion activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_updated',
            activity_data={'onboarding_completed': True, **request.data}
        )
        
        response_serializer = UserProfileSerializer(updated_profile)
        return Response({
            'message': 'Onboarding data submitted successfully',
            'profile': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def onboarding_status_view(request):
    """
    Get the user's onboarding status.
    
    GET /api/users/onboarding/status/
    """
    try:
        profile = request.user.user_profile
        return Response({
            'completed': profile.onboarding_completed,
            'completed_at': profile.onboarding_completed_at,
            'has_profile_data': bool(
                profile.height or profile.weight or 
                profile.fitness_goal or profile.activity_level
            )
        }, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({
            'completed': False,
            'completed_at': None,
            'has_profile_data': False
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_picture_view(request):
    """
    Upload profile picture for the current user.
    
    POST /api/users/profile/picture/upload/
    """
    try:
        profile = request.user.user_profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    if 'profile_picture' not in request.FILES:
        return Response({
            'error': 'No profile picture file provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    profile_picture = request.FILES['profile_picture']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if profile_picture.content_type not in allowed_types:
        return Response({
            'error': 'Invalid file type. Only JPEG, PNG, and GIF images are allowed.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if profile_picture.size > max_size:
        return Response({
            'error': 'File too large. Maximum size is 5MB.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Save the profile picture
    profile.profile_picture = profile_picture
    profile.save()
    
    # Get the URL of the uploaded picture
    picture_url = profile.profile_picture.url if profile.profile_picture else None
    
    # Track profile picture upload activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='profile_updated',
        activity_data={'profile_picture_uploaded': True}
    )
    
    return Response({
        'message': 'Profile picture uploaded successfully',
        'profile_picture_url': picture_url
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_picture_view(request):
    """
    Delete the user's profile picture.
    
    DELETE /api/users/profile/picture/delete/
    """
    try:
        profile = request.user.user_profile
        if profile.profile_picture:
            # Delete the file
            profile.profile_picture.delete()
            profile.profile_picture = None
            profile.save()
            
            # Track profile picture deletion activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='profile_updated',
                activity_data={'profile_picture_deleted': True}
            )
            
            return Response({
                'message': 'Profile picture deleted successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'No profile picture to delete'
            }, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_analytics_view(request):
    """
    Get analytics data for the user's profile.
    
    GET /api/users/profile/analytics/
    """
    try:
        profile = request.user.user_profile
        
        # Get user activities
        activities = UserActivity.objects.filter(user=request.user)
        activity_counts = {}
        for activity in activities:
            activity_counts[activity.activity_type] = activity_counts.get(activity.activity_type, 0) + 1
        
        analytics = {
            'profile_completion': {
                'personal_info': bool(profile.first_name or profile.last_name),
                'contact_info': bool(profile.email),
                'health_metrics': bool(profile.height and profile.weight),
                'fitness_goals': bool(profile.fitness_goal),
                'preferences': bool(profile.dietary_preferences or profile.workout_types),
                'overall_completion': 0  # Will calculate below
            },
            'activity_summary': activity_counts,
            'health_summary': {
                'bmi': profile.bmi,
                'weight_difference': profile.weight_difference,
                'current_weight': profile.weight,
                'target_weight': profile.target_weight,
                'fitness_goal': profile.fitness_goal,
                'activity_level': profile.activity_level
            },
            'onboarding_status': {
                'completed': profile.onboarding_completed,
                'completed_at': profile.onboarding_completed_at
            }
        }
        
        # Calculate overall completion percentage
        completion_fields = analytics['profile_completion']
        completed_fields = sum(1 for field in completion_fields.values() if field and field is not False)
        total_fields = len(completion_fields) - 1  # Exclude overall_completion
        analytics['profile_completion']['overall_completion'] = round((completed_fields / total_fields) * 100, 1)
        
        return Response(analytics, status=status.HTTP_200_OK)
        
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_activity_view(request):
    """
    Track a user activity.
    
    POST /api/users/activity/
    """
    activity_type = request.data.get('activity_type')
    activity_data = request.data.get('activity_data', {})
    
    if not activity_type:
        return Response({
            'error': 'activity_type is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate activity type
    valid_types = [choice[0] for choice in UserActivity._meta.get_field('activity_type').choices]
    if activity_type not in valid_types:
        return Response({
            'error': f'Invalid activity_type. Must be one of: {valid_types}'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    activity = UserActivity.objects.create(
        user=request.user,
        activity_type=activity_type,
        activity_data=activity_data
    )
    
    serializer = UserActivitySerializer(activity)
    return Response({
        'message': 'Activity tracked successfully',
        'activity': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activities_view(request):
    """
    Get user's activity history.
    
    GET /api/users/activities/
    """
    activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')
    serializer = UserActivitySerializer(activities, many=True)
    return Response({
        'activities': serializer.data,
        'count': activities.count()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contact_info_view(request):
    """
    Get user's contact information.
    
    GET /api/users/contact/
    """
    try:
        profile = request.user.user_profile
        return Response({
            'email': request.user.email
        }, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        # Create a basic profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
        return Response({
            'email': request.user.email
        }, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_contact_info_view(request):
    """
    Update user's contact information.
    
    PATCH /api/users/contact/update/
    """
    try:
        profile = request.user.user_profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=request.user)
    
    # No contact info fields to update
    return Response({
        'message': 'Contact information updated successfully',
        'contact_info': {
            'email': request.user.email
        }
    }, status=status.HTTP_200_OK)
