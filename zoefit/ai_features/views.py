"""
Core AI features views for ZoeFit

This module handles the core AI functionality that is shared
across workout and nutrition modules:
- Health profile management and BMI calculations
- AI chatbot for fitness questions and advice
- General progress tracking and AI insights
- Advanced analytics and recommendations

Workout-specific and nutrition-specific endpoints have been moved
to their respective modules for better separation of concerns.
"""

import json
import logging
from datetime import date, timedelta, datetime
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import HealthMetrics, AIChatHistory, ProgressTracking
from .ai_engine import AIRecommendationEngine
from nutrition.models import MealPlan
try:
    from .ml_performance import MLPerformanceLog, MLPredictionFeedback, MLModelMetrics
except ImportError:
    # Fallback if ml_performance module doesn't exist
    MLPerformanceLog = None
    MLPredictionFeedback = None
    MLModelMetrics = None
try:
    from .chatbot import EnhancedAIChatbot
except ImportError:
    EnhancedAIChatbot = None
try:
    from .advanced_ai import AdvancedAIEngine
except ImportError:
    AdvancedAIEngine = None
try:
    from .analytics import AIAnalytics
except ImportError:
    AIAnalytics = None
try:
    from nutrition.ml.ml_engine import ml_nutrition_engine
except ImportError:
    ml_nutrition_engine = None

logger = logging.getLogger(__name__)


def calculate_calories_burned(workout_type, duration_minutes):
    """
    Estimate calories burned based on workout type and duration.
    Uses MET (Metabolic Equivalent of Task) values for different workout types.
    """
    # MET values for different workout types (approximate)
    met_values = {
        'cardio': 8.0,      # Running, cycling, etc.
        'strength': 6.0,    # Weight training
        'hiit': 10.0,       # High-intensity interval training
        'flexibility': 3.0, # Yoga, stretching
        'mixed': 7.0,       # Mixed workout types
    }
    
    # Default MET value if workout type not found
    met_value = met_values.get(workout_type.lower(), 7.0)
    
    # Average user weight (kg) - this could be made more accurate with user profile data
    avg_weight = 70
    
    # Calories = MET × weight (kg) × duration (hours)
    calories = met_value * avg_weight * (duration_minutes / 60)
    
    return int(calories)


@api_view(['GET'])
@permission_classes([AllowAny])
def test_endpoint(request):
    """
    Simple test endpoint to verify server is working.
    """
    return Response({
        'message': 'ZoeFit API is working!',
        'status': 'success',
        'timestamp': datetime.now().isoformat()
    }, status=status.HTTP_200_OK)


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
        height = request.data.get('height')
        weight = request.data.get('weight')
        
        # Calculate BMI if we have both height and weight
        bmi = None
        if height and weight:
            height_in_meters = float(height) / 100
            bmi = round(float(weight) / (height_in_meters ** 2), 2)
        
        metrics, created = HealthMetrics.objects.get_or_create(
            user=user,
            defaults={
                'height': height,
                'weight': weight,
                'bmi': bmi,
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
                    'id': existing_plan.id,
                    'date': existing_plan.date,
                    'meals': existing_plan.meals,
                    'total_calories': existing_plan.total_calories,
                    'protein': existing_plan.protein,
                    'carbs': existing_plan.carbs,
                    'fat': existing_plan.fat,
                    'confidence_score': existing_plan.confidence_score,
                    'approach': existing_plan.approach or 'existing_plan'
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
            confidence_score=meal_plan_data['confidence_score'],
            approach=meal_plan_data.get('approach', 'ml_based')
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
                'confidence_score': meal_plan.confidence_score,
                'approach': meal_plan.approach
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
    Enhanced with conversation memory and context awareness.
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
        
        # Get enhanced conversation history for context awareness
        context_window = getattr(settings, 'AI_CHAT_CONTEXT_WINDOW', 10)
        conversation_history = list(AIChatHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:context_window].values('user_message', 'ai_response', 'intent_detected', 'confidence_score'))
        
        # Process message with enhanced AI chatbot
        ai_provider = getattr(settings, 'AI_PROVIDER_PREFERENCE', 'groq')
        chatbot = EnhancedAIChatbot(ai_provider=ai_provider)
        response_data = chatbot.process_message(message, metrics, conversation_history)
        
        # Save chat history with enhanced data
        chat_history = AIChatHistory.objects.create(
            user=user,
            user_message=message,
            ai_response=response_data['response'],
            intent_detected=response_data['intent'],
            confidence_score=response_data['confidence'],
            ai_provider_used=response_data.get('ai_provider', 'unknown')
        )
        
        # Generate contextual suggestions based on user profile
        suggestions = response_data.get('suggestions', [])
        if metrics:
            # Add personalized suggestions based on user goals
            if metrics.fitness_goal == 'weight_loss' and response_data['intent'] == 'exercise_advice':
                suggestions.extend(["Ask about cardio routines", "Learn about calorie burning exercises"])
            elif metrics.fitness_goal == 'muscle_gain' and response_data['intent'] == 'nutrition_question':
                suggestions.extend(["Ask about protein timing", "Learn about muscle-building foods"])
            elif metrics.fitness_goal == 'endurance' and response_data['intent'] == 'exercise_advice':
                suggestions.extend(["Ask about stamina training", "Learn about endurance workouts"])
        
        return Response({
            'response': response_data['response'],
            'intent': response_data['intent'],
            'confidence': response_data['confidence'],
            'suggestions': suggestions[:5],  # Limit to 5 suggestions
            'ai_provider': response_data.get('ai_provider', 'unknown'),
            'context_used': {
                'has_health_metrics': metrics is not None,
                'conversation_history_count': len(conversation_history),
                'personalized_response': bool(metrics)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        return Response({
            'error': f'Something went wrong while processing your message: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_chat_history(request):
    """
    Clear user's chat history for privacy or fresh start.
    """
    try:
        user = request.user
        
        # Delete all chat history for the user
        deleted_count = AIChatHistory.objects.filter(user=user).delete()[0]
        
        return Response({
            'message': f'Chat history cleared successfully. Deleted {deleted_count} messages.',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        return Response({
            'error': f'Something went wrong while clearing chat history: {str(e)}'
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_progress_entry(request):
    """
    Create a new progress entry for the user.
    """
    try:
        data = request.data
        
        # Create progress tracking entry
        progress = ProgressTracking.objects.create(
            user=request.user,
            weight=data.get('weight'),
            body_fat_percentage=data.get('bodyFat'),
            muscle_mass=data.get('muscleMass'),
            # Add other fields as needed
        )
        
        # Update user's health metrics if weight is provided
        if data.get('weight'):
            try:
                health_metrics = request.user.health_metrics
                health_metrics.weight = data.get('weight')
                health_metrics.save()
            except HealthMetrics.DoesNotExist:
                # Create health metrics if doesn't exist
                HealthMetrics.objects.create(
                    user=request.user,
                    weight=data.get('weight'),
                    height=170,  # Default height
                    bmi=0,
                    fitness_goal='maintenance',
                    activity_level='moderate'
                )
        
        return Response({
            'message': 'Progress entry created successfully',
            'progress_id': progress.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating progress entry: {str(e)}")
        return Response({
            'error': 'Failed to create progress entry',
            'details': str(e)
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
    Creates or updates WorkoutSession entries for tracking.
    """
    try:
        workout_id = request.data.get('workout_plan_id')  # Updated to match frontend
        completed = request.data.get('completed', True)
        completion_time_minutes = request.data.get('completion_time_minutes')
        rating = request.data.get('rating')
        exercises_completed = request.data.get('exercises_completed', [])
        workout_type = request.data.get('workout_type', 'Workout')  # Get workout type for default workouts
        
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
        from frontend.models import WorkoutSession
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
            }
            
            if completion_time_minutes:
                session_data['duration'] = timedelta(minutes=completion_time_minutes)
            if rating:
                session_data['difficulty_rating'] = rating
            
            session = WorkoutSession.objects.create(**session_data)
        
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
            'error': f'Something went wrong while getting user analytics: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_advanced_ml_analytics(request, period_days):
    """
    Get advanced ML analytics with predictive insights and adaptation status.
    """
    try:
        user = request.user
        period = int(period_days)
        
        # Get basic performance metrics
        performance_logs = MLPerformanceLog.objects.filter(
            user=user,
            created_at__gte=datetime.now() - timedelta(days=period)
        )
        
        # Calculate performance metrics
        total_predictions = performance_logs.count()
        successful_predictions = performance_logs.filter(success=True).count()
        success_rate = successful_predictions / total_predictions if total_predictions > 0 else 0
        
        avg_confidence = performance_logs.aggregate(
            avg_confidence=Avg('confidence_score')
        )['avg_confidence'] or 0
        
        avg_processing_time = performance_logs.aggregate(
            avg_time=Avg('processing_time')
        )['avg_time'] or 0
        
        # Get user feedback metrics
        feedbacks = MLPredictionFeedback.objects.filter(
            performance_log__user=user,
            created_at__gte=datetime.now() - timedelta(days=period)
        )
        
        avg_user_rating = feedbacks.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0
        
        satisfied_users = feedbacks.filter(rating__gte=4).count()
        user_satisfaction = satisfied_users / feedbacks.count() if feedbacks.count() > 0 else 0
        
        # Calculate approach distribution
        approach_distribution = performance_logs.values('approach').annotate(
            count=Count('approach')
        ).order_by('-count')
        
        approach_counts = {}
        for item in approach_distribution:
            approach_counts[item['approach']] = item['count']
        
        # Get ML vs Rule comparison
        ml_logs = performance_logs.filter(approach='ml_based')
        rule_logs = performance_logs.filter(approach='rule_based')
        
        ml_success_rate = ml_logs.filter(success=True).count() / ml_logs.count() if ml_logs.count() > 0 else 0
        rule_success_rate = rule_logs.filter(success=True).count() / rule_logs.count() if rule_logs.count() > 0 else 0
        
        ml_feedbacks = feedbacks.filter(performance_log__approach='ml_based')
        rule_feedbacks = feedbacks.filter(performance_log__approach='rule_based')
        
        ml_avg_rating = ml_feedbacks.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        rule_avg_rating = rule_feedbacks.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        ml_avg_confidence = ml_logs.aggregate(avg_confidence=Avg('confidence_score'))['avg_confidence'] or 0
        rule_avg_confidence = rule_logs.aggregate(avg_confidence=Avg('confidence_score'))['avg_confidence'] or 0
        
        # Get user's health metrics for predictive insights
        try:
            metrics = HealthMetrics.objects.filter(user=user).latest('created_at')
            
            # Generate predictive insights using ML engine
            insights = ml_nutrition_engine._generate_predictive_insights(metrics, date.today())
            
            # Get adaptation status
            recent_feedback = feedbacks.order_by('-timestamp')[:10]
            adaptation_active = len(recent_feedback) >= 10
            
            adaptation_factor = 0
            if adaptation_active and recent_feedback:
                avg_rating = recent_feedback.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
                adaptation_factor = avg_rating / 5.0  # Normalize to 0-1
            
            last_adaptation = 'Recently' if adaptation_active else 'Never'
            
        except HealthMetrics.DoesNotExist:
            insights = {
                'trend_analysis': {'status': 'no_data', 'message': 'No health metrics available'},
                'goal_projection': {'status': 'no_data', 'message': 'No health metrics available'},
                'recommendation_trends': {'status': 'no_data', 'message': 'No health metrics available'},
                'seasonal_insights': {'status': 'no_data', 'message': 'No health metrics available'},
                'performance_forecast': {'status': 'no_data', 'message': 'No health metrics available'}
            }
            adaptation_active = False
            adaptation_factor = 0
            last_adaptation = 'Never'
        
        response_data = {
            'performance_metrics': {
                'total_predictions': total_predictions,
                'success_rate': success_rate,
                'avg_confidence': avg_confidence,
                'avg_user_rating': avg_user_rating,
                'user_satisfaction': user_satisfaction,
                'avg_processing_time': avg_processing_time
            },
            'approach_distribution': {
                'ml_based': approach_counts.get('ml_based', 0),
                'rule_based': approach_counts.get('rule_based', 0),
                'hybrid': approach_counts.get('hybrid', 0),
                'emergency_fallback': approach_counts.get('emergency_fallback', 0)
            },
            'ml_vs_rule_comparison': {
                'ml_success_rate': ml_success_rate,
                'rule_success_rate': rule_success_rate,
                'ml_avg_rating': ml_avg_rating,
                'rule_avg_rating': rule_avg_rating,
                'ml_avg_confidence': ml_avg_confidence,
                'rule_avg_confidence': rule_avg_confidence
            },
            'predictive_insights': insights,
            'adaptation_status': {
                'adaptation_active': adaptation_active,
                'adaptation_factor': adaptation_factor,
                'feedback_count': len(recent_feedback) if 'recent_feedback' in locals() else 0,
                'last_adaptation': last_adaptation
            }
        }
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"Error in get_advanced_ml_analytics: {str(e)}")
        return Response({
            'error': f'Failed to load advanced analytics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            'error': f'Something went wrong while getting system analytics: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


# ============= WORKOUT PREFERENCES API =============
# NOTE: WorkoutPreferences functionality has been removed
# Users can now set preferences directly through their profile
