"""
Workout module views for ZoeFit

This module handles all workout-related API endpoints:
- Workout plan generation and management
- Workout preferences and equipment
- Workout session tracking and completion
- Workout progress and performance analytics

These views are specifically focused on workout functionality
and provide clean separation from nutrition features.
"""

import json
from datetime import date, timedelta, datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import WorkoutPlan, WorkoutSession, WorkoutProgress
from ai_features.models import HealthMetrics
from ai_features.ai_engine import AIRecommendationEngine


def calculate_calories_burned(workout_type, duration_minutes):
    """
    Estimate calories burned based on workout type and duration.
    Uses MET (Metabolic Equivalent of Task) values for different workout types.
    """
    met_values = {
        'cardio': 8.0,      # Running, cycling, etc.
        'strength': 6.0,    # Weight training
        'hiit': 10.0,       # High-intensity interval training
        'flexibility': 3.0, # Yoga, stretching
        'mixed': 7.0,       # Mixed workout types
    }
    
    met_value = met_values.get(workout_type.lower(), 7.0)
    avg_weight = 70  # Average user weight (kg)
    
    # Calories = MET × weight (kg) × duration (hours)
    calories = met_value * avg_weight * (duration_minutes / 60)
    
    return int(calories)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_workout_plan(request):
    """
    Generate AI-powered workout plan based on user's fitness level and goals.
    """
    try:
        user = request.user
        day_number = request.data.get('day', 1)
        
        # Get user's health metrics
        metrics = get_object_or_404(HealthMetrics, user=user)
        
        # Check if workout plan already exists for this day
        existing_plan = WorkoutPlan.objects.filter(user=user, day=day_number).first()
        if existing_plan:
            return Response({
                'message': 'Workout plan already exists for this day',
                'workout_plan': {
                    'id': existing_plan.id,
                    'day': existing_plan.day,
                    'exercises': existing_plan.exercises,
                    'workout_type': existing_plan.workout_type,
                    'estimated_duration': existing_plan.estimated_duration,
                    'difficulty_level': existing_plan.difficulty_level,
                    'intensity_score': existing_plan.intensity_score,
                    'equipment_needed': existing_plan.equipment_needed
                }
            }, status=status.HTTP_200_OK)
        
        # Generate workout plan using AI engine with preferences
        ai_engine = AIRecommendationEngine()
        workout_plan_data = ai_engine.generate_workout_plan(metrics, day_number, preferences)
        
        # Create workout plan record
        workout_plan = WorkoutPlan.objects.create(
            user=user,
            day=day_number,
            exercises=workout_plan_data['exercises'],
            workout_type=workout_plan_data['workout_type'],
            estimated_duration=workout_plan_data['estimated_duration'],
            difficulty_level=workout_plan_data['difficulty_level'],
            intensity_score=workout_plan_data['intensity_score'],
            adaptation_score=workout_plan_data['adaptation_score'],
            equipment_needed=workout_plan_data.get('equipment_needed', [])
        )
        
        return Response({
            'message': 'Workout plan generated successfully',
            'workout_plan': {
                'id': workout_plan.id,
                'day': workout_plan.day,
                'exercises': workout_plan.exercises,
                'workout_type': workout_plan.workout_type,
                'estimated_duration': workout_plan.estimated_duration,
                'difficulty_level': workout_plan.difficulty_level,
                'intensity_score': workout_plan.intensity_score,
                'equipment_needed': workout_plan.equipment_needed,
                'adaptation_score': workout_plan.adaptation_score
            }
        }, status=status.HTTP_201_CREATED)
        
    except HealthMetrics.DoesNotExist:
        return Response({
            'error': 'Health metrics not found. Please create your health profile first.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Something went wrong while generating workout plan: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workout_plans(request):
    """
    Get user's workout plans.
    """
    try:
        workout_plans = WorkoutPlan.objects.filter(
            user=request.user
        ).order_by('day')
        
        plans_data = []
        for plan in workout_plans:
            plans_data.append({
                'id': plan.id,
                'day': plan.day,
                'exercises': plan.exercises,
                'workout_type': plan.workout_type,
                'estimated_duration': plan.estimated_duration,
                'difficulty_level': plan.difficulty_level,
                'intensity_score': plan.intensity_score,
                'equipment_needed': plan.equipment_needed,
                'completed': plan.completed,
                'completion_time': plan.completion_time,
                'user_rating': plan.user_rating
            })
        
        return Response({
            'workout_plans': plans_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while fetching workout plans: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_workout_completion(request):
    """
    Update workout completion status and time.
    Creates or updates WorkoutSession entries for tracking.
    """
    try:
        workout_id = request.data.get('workout_plan_id')
        completed = request.data.get('completed', True)
        completion_time_minutes = request.data.get('completion_time_minutes')
        rating = request.data.get('rating')
        exercises_completed = request.data.get('exercises_completed', [])
        workout_type = request.data.get('workout_type', 'Workout')
        
        workout_plan = None
        if workout_id:
            try:
                workout_plan = WorkoutPlan.objects.get(id=workout_id, user=request.user)
            except WorkoutPlan.DoesNotExist:
                return Response({
                    'error': 'Workout plan not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        if workout_plan:
            workout_plan.completed = completed
            if completion_time_minutes:
                workout_plan.completion_time = timedelta(minutes=completion_time_minutes)
            if rating:
                workout_plan.user_rating = rating
            workout_plan.save()
        
        # Create or update WorkoutSession for proper tracking
        from django.utils import timezone
        
        # Check if a session already exists for this workout plan today
        today = timezone.now().date()
        existing_session = WorkoutSession.objects.filter(
            user=request.user,
            workout_plan=workout_plan,
            start_time__date=today
        ).first()
        
        if existing_session:
            # Update existing session
            existing_session.completed = completed
            if completion_time_minutes:
                existing_session.duration = timedelta(minutes=completion_time_minutes)
                existing_session.end_time = existing_session.start_time + existing_session.duration
            if exercises_completed:
                existing_session.exercises_completed = exercises_completed
            if rating:
                existing_session.difficulty_rating = rating
            
            # Calculate calories based on workout type and duration
            if completion_time_minutes:
                workout_type_for_calc = workout_plan.workout_type if workout_plan else workout_type
                calories = calculate_calories_burned(workout_type_for_calc, completion_time_minutes)
                existing_session.calories_burned = calories
            
            existing_session.save()
        else:
            # Create new session
            start_time = timezone.now() - timedelta(minutes=completion_time_minutes or 0)
            end_time = timezone.now() if completed else None
            
            calories = 0
            if completion_time_minutes:
                workout_type_for_calc = workout_plan.workout_type if workout_plan else workout_type
                calories = calculate_calories_burned(workout_type_for_calc, completion_time_minutes)
            
            session_data = {
                'user': request.user,
                'workout_plan': workout_plan,
                'start_time': start_time,
                'end_time': end_time,
                'completed': completed,
                'exercises_completed': exercises_completed,
                'calories_burned': calories,
                'workout_type': workout_plan.workout_type if workout_plan else workout_type
            }
            
            if completion_time_minutes:
                session_data['duration'] = timedelta(minutes=completion_time_minutes)
            if rating:
                session_data['difficulty_rating'] = rating
            
            session = WorkoutSession.objects.create(**session_data)
        
        # Update workout progress
        if completed:
            progress, created = WorkoutProgress.objects.get_or_create(
                user=request.user,
                defaults={
                    'total_workouts': 1,
                    'workout_streak': 1
                }
            )
            
            if not created:
                progress.total_workouts += 1
                progress.workout_streak += 1
                if completion_time_minutes:
                    progress.total_workout_time += timedelta(minutes=completion_time_minutes)
                progress.total_calories_burned += calories
                progress.save()
        
        return Response({
            'message': 'Workout completion updated successfully'
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating workout completion: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workout_sessions(request):
    """
    Get user's workout session history.
    """
    try:
        days = int(request.GET.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        sessions = WorkoutSession.objects.filter(
            user=request.user,
            start_time__gte=start_date
        ).order_by('-start_time')
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'workout_plan_id': session.workout_plan.id if session.workout_plan else None,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'duration': session.duration,
                'workout_type': session.workout_type,
                'completed': session.completed,
                'calories_burned': session.calories_burned,
                'difficulty_rating': session.difficulty_rating,
                'exercises_completed': session.exercises_completed,
                'notes': session.notes
            })
        
        return Response({
            'workout_sessions': sessions_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while fetching workout sessions: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workout_progress(request):
    """
    Get user's workout progress and performance metrics.
    """
    try:
        progress_data = WorkoutProgress.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]  # Last 10 entries
        
        progress_list = []
        for progress in progress_data:
            progress_list.append({
                'id': progress.id,
                'total_workouts': progress.total_workouts,
                'workout_streak': progress.workout_streak,
                'total_workout_time': progress.total_workout_time,
                'total_calories_burned': progress.total_calories_burned,
                'performance_score': progress.performance_score,
                'achievement_badges': progress.achievement_badges,
                'ai_insights': progress.ai_insights,
                'created_at': progress.created_at
            })
        
        return Response({
            'workout_progress': progress_list
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while fetching workout progress: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def adapt_workout_plan(request):
    """
    Adapt workout plan based on user performance data.
    """
    try:
        user = request.user
        workout_id = request.data.get('workout_id')
        performance_data = request.data.get('performance_data', {})
        
        # Get workout plan
        workout_plan = get_object_or_404(WorkoutPlan, id=workout_id, user=user)
        
        # For now, this is a placeholder for advanced AI adaptation
        # In a full implementation, this would use the AdvancedAIEngine
        # to modify the workout based on performance data
        
        return Response({
            'message': 'Workout adaptation feature coming soon',
            'current_plan': {
                'id': workout_plan.id,
                'exercises': workout_plan.exercises,
                'intensity_score': workout_plan.intensity_score,
                'difficulty_level': workout_plan.difficulty_level
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while adapting workout plan: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
