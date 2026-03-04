"""
User profile API endpoints for ZoeFit

This module handles all the profile-related API calls:
- Getting your current profile
- Creating a new profile
- Updating your information
- Deleting your profile

These endpoints are designed to be straightforward and user-friendly.
We validate all input data and provide helpful error messages
so users know exactly what to fix.

Profile management is separate from authentication - users can exist
without profiles, but profiles give them a personalized experience.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserProfile
from .serializers import UserProfileSerializer, UserProfileCreateSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get the current user's profile information.
    
    Returns all the profile data we have for this user,
    including their name, photo, bio, and fitness goals.

     GET /api/profiles/profile/

    If the user hasn't created a profile yet, we let them know
    so they can create one to get the full ZoeFit experience.
    """
    try:
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found. Please create a profile first.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_profile_view(request):
    """
    Create a new profile for the authenticated user.
    
    POST /api/profiles/profile/create/

    Users can create their profile with whatever information
    they're comfortable sharing. All fields are optional
    except the basic connection to their user account.
    
    Once created, users can update their profile anytime.
    We validate the data and make sure everything looks good
    before saving it to the database.
    """
    # Check if user already has a profile
    if hasattr(request.user, 'profile'):
        return Response({
            'error': 'You already have a profile. Use the update endpoint to make changes.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserProfileCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        profile = serializer.save(user=request.user)
        response_serializer = UserProfileSerializer(profile)
        return Response({
            'message': 'Your profile has been created successfully!',
            'profile': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user's profile.
    
    PUT/PATCH /api/profiles/profile/update/
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found. Please create a profile first.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserProfileSerializer(
        profile,
        data=request.data,
        partial=True  # Allow partial updates for PATCH
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_profile_view(request):
    """
    Delete current user's profile.
    
    DELETE /api/profiles/profile/delete/
    """
    try:
        profile = request.user.profile
        profile.delete()
        return Response({
            'message': 'Profile deleted successfully'
        }, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
