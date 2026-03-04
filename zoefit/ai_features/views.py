"""
AI-powered fitness API endpoints for ZoeFit

This module handles all the AI features that make ZoeFit smart:
- Health profile management and BMI calculations
- Personalized meal planning based on dietary needs
- Custom workout generation that adapts to user progress
- AI chatbot for fitness questions and advice
- Progress tracking and predictive insights
- Advanced analytics and recommendations

Our AI uses machine learning to understand each user's unique needs
and provides personalized recommendations that actually work.

Each endpoint is designed to be fast, reliable, and user-friendly.
We handle errors gracefully and provide helpful error messages
so users know what to do next.
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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import (
    HealthMetrics, MealPlan, WorkoutPlan, 
    AIChatHistory, ProgressTracking
)
from .ai_engine import AIRecommendationEngine
from .enhanced_chatbot import EnhancedAIChatbot
from .advanced_ai import AdvancedAIEngine
from .analytics import AIAnalytics


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_health_metrics(request):
    """
    Set up or update a user's health profile.
    
    This is the foundation of our AI system - we need to know
    about the user before we can make good recommendations.
    
    Users can update their profile anytime:
    - Height and weight for BMI calculations
    - Fitness goals (weight loss, muscle gain, etc.)
    - Activity level (how much they exercise)
    - Dietary preferences and restrictions
    - Medical conditions and allergies
    
    We automatically calculate BMI and daily calorie needs,
    which helps our AI create better meal and workout plans.
    """
    try:
        user = request.user
        
        # Get existing metrics or create new ones
        metrics, created = HealthMetrics.objects.get_or_create(
            user=user,
            defaults={
                'height': request.data.get('height'),
                'weight': request.data.get('weight'),
                'fitness_goal': request.data.get('fitness_goal', 'maintenance'),
                'activity_level': request.data.get('activity_level', 'moderate'),
                'dietary_preferences': request.data.get('dietary_preferences', {}),
                'medical_conditions': request.data.get('medical_conditions', []),
                'allergies': request.data.get('allergies', []),
                'target_weight': request.data.get('target_weight'),
            }
        )
        
        if not created:
            # Update existing profile with new data
            metrics.height = request.data.get('height', metrics.height)
            metrics.weight = request.data.get('weight', metrics.weight)
            metrics.fitness_goal = request.data.get('fitness_goal', metrics.fitness_goal)
            metrics.activity_level = request.data.get('activity_level', metrics.activity_level)
            metrics.dietary_preferences = request.data.get('dietary_preferences', metrics.dietary_preferences)
            metrics.medical_conditions = request.data.get('medical_conditions', metrics.medical_conditions)
            metrics.allergies = request.data.get('allergies', metrics.allergies)
            metrics.target_weight = request.data.get('target_weight', metrics.target_weight)
        
        # Auto-calculate BMI if we have height and weight
        if metrics.height and metrics.weight:
            metrics.bmi = metrics.calculate_bmi()
        
        metrics.save()
        
        return Response({
            'message': 'Your health profile has been updated successfully!',
            'metrics': {
                'height': metrics.height,
                'weight': metrics.weight,
                'bmi': metrics.bmi,
                'bmi_category': metrics.get_bmi_category(),
                'fitness_goal': metrics.fitness_goal,
                'activity_level': metrics.activity_level,
                'daily_calories': metrics.calculate_daily_calories()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_health_metrics(request):
    """
    Get the user's current health profile.
    
    Returns all the health data we have for this user,
    including calculated values like BMI and daily calories.
    
    This is used by the frontend to display the user's profile
    and by the AI to generate personalized recommendations.
    """
    try:
        metrics = get_object_or_404(HealthMetrics, user=request.user)
        
        return Response({
            'height': metrics.height,
            'weight': metrics.weight,
            'bmi': metrics.bmi,
            'bmi_category': metrics.get_bmi_category(),
            'fitness_goal': metrics.fitness_goal,
            'activity_level': metrics.activity_level,
            'dietary_preferences': metrics.dietary_preferences,
            'medical_conditions': metrics.medical_conditions,
            'allergies': metrics.allergies,
            'target_weight': metrics.target_weight,
            'daily_calories': metrics.calculate_daily_calories(),
            'created_at': metrics.created_at,
            'updated_at': metrics.updated_at
        })
        
    except HealthMetrics.DoesNotExist:
        return Response({
            'error': 'Health metrics not found. Please create your health profile first.'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_meal_plan(request):
    """
    Generate AI-powered meal plan based on user's health metrics and preferences.
    """
    try:
        user = request.user
        target_date = request.data.get('date', date.today())
        
        # Get user's health metrics
        metrics = get_object_or_404(HealthMetrics, user=user)
        
        # Check if meal plan already exists for this date
        existing_plan = MealPlan.objects.filter(user=user, date=target_date).first()
        if existing_plan:
            return Response({
                'message': 'Meal plan already exists for this date',
                'meal_plan': {
                    'date': existing_plan.date,
                    'meals': existing_plan.meals,
                    'total_calories': existing_plan.total_calories,
                    'protein': existing_plan.protein,
                    'carbs': existing_plan.carbs,
                    'fat': existing_plan.fat
                }
            }, status=status.HTTP_200_OK)
        
        # Generate meal plan using AI engine
        ai_engine = AIRecommendationEngine()
        meal_plan_data = ai_engine.generate_meal_plan(metrics, target_date)
        
        # Create meal plan record
        meal_plan = MealPlan.objects.create(
            user=user,
            date=target_date,
            meals=meal_plan_data['meals'],
            total_calories=meal_plan_data['total_calories'],
            protein=meal_plan_data['protein'],
            carbs=meal_plan_data['carbs'],
            fat=meal_plan_data['fat'],
            confidence_score=meal_plan_data['confidence_score']
        )
        
        return Response({
            'message': 'Meal plan generated successfully',
            'meal_plan': {
                'id': meal_plan.id,
                'date': meal_plan.date,
                'meals': meal_plan.meals,
                'total_calories': meal_plan.total_calories,
                'protein': meal_plan.protein,
                'carbs': meal_plan.carbs,
                'fat': meal_plan.fat,
                'confidence_score': meal_plan.confidence_score
            }
        }, status=status.HTTP_201_CREATED)
        
    except HealthMetrics.DoesNotExist:
        return Response({
            'error': 'Health metrics not found. Please create your health profile first.'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_meal_plans(request):
    """
    Get user's meal plans for a date range.
    """
    try:
        start_date = request.GET.get('start_date', date.today() - timedelta(days=7))
        end_date = request.GET.get('end_date', date.today() + timedelta(days=7))
        
        meal_plans = MealPlan.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        plans_data = []
        for plan in meal_plans:
            plans_data.append({
                'id': plan.id,
                'date': plan.date,
                'meals': plan.meals,
                'total_calories': plan.total_calories,
                'protein': plan.protein,
                'carbs': plan.carbs,
                'fat': plan.fat,
                'user_rating': plan.user_rating,
                'user_feedback': plan.user_feedback
            })
        
        return Response({
            'meal_plans': plans_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


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
                    'day': existing_plan.day,
                    'exercises': existing_plan.exercises,
                    'workout_type': existing_plan.workout_type,
                    'estimated_duration': existing_plan.estimated_duration,
                    'difficulty_level': existing_plan.difficulty_level,
                    'intensity_score': existing_plan.intensity_score,
                    'equipment_needed': existing_plan.equipment_needed
                }
            }, status=status.HTTP_200_OK)
        
        # Generate workout plan using AI engine
        ai_engine = AIRecommendationEngine()
        workout_plan_data = ai_engine.generate_workout_plan(metrics, day_number)
        
        # Create workout plan record
        workout_plan = WorkoutPlan.objects.create(
            user=user,
            day=day_number,
            exercises=workout_plan_data['exercises'],
            workout_type=workout_plan_data['workout_type'],
            estimated_duration=workout_plan_data['estimated_duration'],
            difficulty_level=workout_plan_data['difficulty_level'],
            intensity_score=workout_plan_data['intensity_score'],
            equipment_needed=workout_plan_data['equipment_needed'],
            adaptation_score=workout_plan_data['adaptation_score']
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
            'error': f'Something went wrong while updating your profile: {str(e)}'
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
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """
    AI chatbot endpoint for fitness-related questions and advice.
    """
    try:
        user = request.user
        message = request.data.get('message', '')
        
        if not message.strip():
            return Response({
                'error': 'Message cannot be empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's health metrics for personalized responses
        try:
            metrics = HealthMetrics.objects.get(user=user)
        except HealthMetrics.DoesNotExist:
            metrics = None
        
        # Process message with enhanced AI chatbot
        from django.conf import settings
        ai_provider = getattr(settings, 'AI_PROVIDER_PREFERENCE', 'auto')
        chatbot = EnhancedAIChatbot(ai_provider=ai_provider)
        response_data = chatbot.process_message(message, metrics)
        
        # Save chat history
        chat_history = AIChatHistory.objects.create(
            user=user,
            user_message=message,
            ai_response=response_data['response'],
            intent_detected=response_data['intent'],
            confidence_score=response_data['confidence']
        )
        
        return Response({
            'response': response_data['response'],
            'intent': response_data['intent'],
            'confidence': response_data['confidence'],
            'suggestions': response_data.get('suggestions', [])
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    """
    Get user's AI chat history.
    """
    try:
        limit = int(request.GET.get('limit', 50))
        chat_history = AIChatHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[:limit]
        
        history_data = []
        for chat in chat_history:
            history_data.append({
                'id': chat.id,
                'user_message': chat.user_message,
                'ai_response': chat.ai_response,
                'intent_detected': chat.intent_detected,
                'confidence_score': chat.confidence_score,
                'helpful': chat.helpful,
                'created_at': chat.created_at
            })
        
        return Response({
            'chat_history': history_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_progress_tracking(request):
    """
    Get user's progress tracking data and AI insights.
    """
    try:
        progress_data = ProgressTracking.objects.filter(
            user=request.user
        ).order_by('-created_at')[:30]  # Last 30 entries
        
        progress_list = []
        for progress in progress_data:
            progress_list.append({
                'id': progress.id,
                'weight': progress.weight,
                'body_fat_percentage': progress.body_fat_percentage,
                'muscle_mass': progress.muscle_mass,
                'workout_streak': progress.workout_streak,
                'total_workouts': progress.total_workouts,
                'calories_burned': progress.calories_burned,
                'progress_score': progress.progress_score,
                'achievement_badges': progress.achievement_badges,
                'ai_insights': progress.ai_insights,
                'created_at': progress.created_at
            })
        
        return Response({
            'progress_data': progress_list
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_workout_completion(request):
    """
    Update workout completion status and time.
    """
    try:
        workout_id = request.data.get('workout_id')
        completed = request.data.get('completed', True)
        completion_time_minutes = request.data.get('completion_time_minutes')
        rating = request.data.get('rating')
        
        workout_plan = get_object_or_404(WorkoutPlan, id=workout_id, user=request.user)
        
        workout_plan.completed = completed
        if completion_time_minutes:
            from datetime import timedelta
            workout_plan.completion_time = timedelta(minutes=completion_time_minutes)
        if rating:
            workout_plan.user_rating = rating
        
        workout_plan.save()
        
        # Update progress tracking
        if completed:
            progress, created = ProgressTracking.objects.get_or_create(
                user=request.user,
                defaults={
                    'total_workouts': 1,
                    'workout_streak': 1
                }
            )
            
            if not created:
                progress.total_workouts += 1
                progress.workout_streak += 1
                progress.save()
        
        return Response({
            'message': 'Workout completion updated successfully'
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def predict_progress(request):
    """
    Predict user's progress over the next N days.
    """
    try:
        user = request.user
        days_ahead = int(request.GET.get('days', 30))
        
        # Ensure user has health metrics
        try:
            metrics = HealthMetrics.objects.get(user=user)
        except HealthMetrics.DoesNotExist:
            return Response({
                'error': 'Health metrics not found. Please create your health profile first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Generate predictions
        advanced_ai = AdvancedAIEngine()
        predictions = advanced_ai.predict_progress(user, days_ahead)
        
        return Response({
            'predictions': predictions,
            'prediction_period_days': days_ahead,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
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
        
        # Adapt workout plan
        advanced_ai = AdvancedAIEngine()
        adapted_plan = advanced_ai.adapt_workout_plan(user, workout_plan, performance_data)
        
        return Response({
            'message': 'Workout plan adapted successfully',
            'adapted_plan': {
                'id': adapted_plan.id,
                'exercises': adapted_plan.exercises,
                'intensity_score': adapted_plan.intensity_score,
                'difficulty_level': adapted_plan.difficulty_level
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ai_insights(request):
    """
    Get comprehensive AI insights and recommendations.
    """
    try:
        user = request.user
        
        # Get user data
        try:
            metrics = HealthMetrics.objects.get(user=user)
        except HealthMetrics.DoesNotExist:
            return Response({
                'error': 'Health metrics not found. Please create your health profile first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get progress data
        progress_data = ProgressTracking.objects.filter(user=user).order_by('-created_at')[:10]
        
        # Generate insights
        insights = {
            'current_status': {
                'bmi_category': metrics.get_bmi_category(),
                'fitness_goal': metrics.fitness_goal,
                'activity_level': metrics.activity_level,
                'daily_calories': metrics.calculate_daily_calories()
            },
            'progress_summary': {
                'total_workouts': sum(p.total_workouts for p in progress_data) if progress_data else 0,
                'current_streak': progress_data[0].workout_streak if progress_data else 0,
                'latest_weight': progress_data[0].weight if progress_data and progress_data[0].weight else metrics.weight
            },
            'recommendations': [],
            'achievements': []
        }
        
        # Add personalized recommendations
        if progress_data:
            latest = progress_data[0]
            if latest.workout_streak >= 7:
                insights['recommendations'].append("Excellent consistency! Consider increasing workout intensity.")
            elif latest.workout_streak < 3:
                insights['recommendations'].append("Try to maintain at least 3 workouts per week for better results.")
            
            if latest.progress_score > 80:
                insights['achievements'].append("High Progress Score - Keep up the great work!")
        
        # Add goal-specific advice
        if metrics.fitness_goal == 'weight_loss':
            insights['recommendations'].append("Focus on creating a sustainable calorie deficit.")
        elif metrics.fitness_goal == 'muscle_gain':
            insights['recommendations'].append("Ensure adequate protein intake and progressive overload.")
        
        return Response({
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_analytics(request):
    """
    Get comprehensive user engagement and behavior analytics.
    """
    try:
        user = request.user
        days = int(request.GET.get('days', 30))
        
        analytics = AIAnalytics()
        user_analytics = analytics.get_user_engagement_metrics(user, days)
        behavior_insights = analytics.get_user_behavior_insights(user)
        
        return Response({
            'engagement_metrics': user_analytics,
            'behavior_insights': behavior_insights,
            'analytics_period_days': days
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_system_analytics(request):
    """
    Get AI system performance metrics (admin only).
    """
    try:
        # Check if user is admin/staff
        if not request.user.is_staff:
            return Response({
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        days = int(request.GET.get('days', 30))
        
        analytics = AIAnalytics()
        ai_performance = analytics.get_ai_performance_metrics(days)
        system_health = analytics.get_system_health_metrics()
        
        return Response({
            'ai_performance': ai_performance,
            'system_health': system_health,
            'analytics_period_days': days
        })
        
    except Exception as e:
        return Response({
            'error': f'Something went wrong while updating your profile: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
