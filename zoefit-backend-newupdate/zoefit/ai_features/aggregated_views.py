"""
Aggregated views for common frontend operations.

These views provide consolidated data from multiple modules to reduce
the number of API calls needed by the frontend and ensure data consistency.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from datetime import timedelta

from .services import ProgressSyncService, UserDataAggregationService
from workout.models import WorkoutPlan, WorkoutSession
from nutrition.models import MealPlan, NutritionLog

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    """
    Get comprehensive dashboard data for the authenticated user.
    
    This endpoint consolidates data from health metrics, progress tracking,
    recent workouts, and meal plans into a single response.
    """
    try:
        dashboard_data = UserDataAggregationService.get_user_dashboard_data(request.user)
        return Response(dashboard_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Failed to load dashboard data', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_summary(request):
    """
    Get summary statistics for the authenticated user.
    
    Provides key metrics and achievements across all modules.
    """
    try:
        summary_stats = UserDataAggregationService.get_user_summary_stats(request.user)
        return Response(summary_stats, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Failed to load summary statistics', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_progress(request):
    """
    Manually trigger progress synchronization.
    
    This endpoint forces an update of the ProgressTracking model
    with the latest data from workout and nutrition modules.
    """
    try:
        progress = ProgressSyncService.update_user_progress(request.user)
        
        return Response({
            'message': 'Progress synchronized successfully',
            'progress_score': progress.progress_score,
            'workout_streak': progress.workout_streak,
            'nutrition_adherence': progress.nutrition_adherence,
            'ai_insights': progress.ai_insights,
            'achievement_badges': progress.achievement_badges,
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Failed to synchronize progress', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_overview(request):
    """
    Get today's overview including workout and meal plan.
    
    This endpoint provides what the user needs to know for today:
    - Today's workout (if scheduled)
    - Today's meal plan
    - Recent progress
    """
    try:
        user = request.user
        today = timezone.now().date()
        
        # Get today's workout
        today_workout = WorkoutPlan.objects.filter(
            user=user,
            day__lte=today,
            completed=False
        ).order_by('day').first()
        
        # Get today's meal plan
        today_meal = MealPlan.objects.filter(
            user=user,
            date=today
        ).first()
        
        # Get recent progress
        progress = ProgressSyncService.update_user_progress(user)
        
        # Get recent workout sessions (last 7 days)
        seven_days_ago = today - timedelta(days=7)
        recent_sessions = WorkoutSession.objects.filter(
            user=user,
            start_time__date__gte=seven_days_ago,
            completed=True
        ).order_by('-start_time')
        
        # Get recent nutrition logs (last 7 days)
        recent_logs = NutritionLog.objects.filter(
            user=user,
            date__gte=seven_days_ago
        ).order_by('-date')
        
        overview_data = {
            'date': today.isoformat(),
            'workout': {
                'scheduled': bool(today_workout),
                'details': {
                    'day': today_workout.day,
                    'type': today_workout.workout_type,
                    'duration': today_workout.estimated_duration,
                    'difficulty': today_workout.difficulty_level,
                    'exercises': today_workout.exercises,
                } if today_workout else None
            },
            'nutrition': {
                'meal_plan_available': bool(today_meal),
                'details': {
                    'meals': today_meal.meals,
                    'total_calories': today_meal.total_calories,
                    'protein': today_meal.protein,
                    'carbs': today_meal.carbs,
                    'fat': today_meal.fat,
                } if today_meal else None
            },
            'recent_activity': {
                'workouts_this_week': recent_sessions.count(),
                'calories_burned_this_week': sum(s.calories_burned for s in recent_sessions),
                'nutrition_days_logged': recent_logs.count(),
                'avg_daily_calories': recent_logs.aggregate(
                    avg_calories=models.Avg('total_calories')
                )['avg_calories'] or 0 if recent_logs.exists() else 0,
            },
            'progress_summary': {
                'current_streak': progress.workout_streak,
                'progress_score': progress.progress_score,
                'nutrition_adherence': progress.nutrition_adherence,
                'insights': progress.ai_insights,
            }
        }
        
        return Response(overview_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Failed to load today\'s overview', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_report(request):
    """
    Get weekly progress report.
    
    Provides a comprehensive view of the user's progress over the past week
    including workouts, nutrition, and overall trends.
    """
    try:
        user = request.user
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Get workout plans for this week
        week_workouts = WorkoutPlan.objects.filter(
            user=user,
            day__gte=week_start.day,
            day__lte=week_end.day
        ).order_by('day')
        
        # Get workout sessions for this week
        week_sessions = WorkoutSession.objects.filter(
            user=user,
            start_time__date__gte=week_start,
            start_time__date__lte=week_end,
            completed=True
        ).order_by('start_time')
        
        # Get meal plans for this week
        week_meals = MealPlan.objects.filter(
            user=user,
            date__gte=week_start,
            date__lte=week_end
        ).order_by('date')
        
        # Get nutrition logs for this week
        week_logs = NutritionLog.objects.filter(
            user=user,
            date__gte=week_start,
            date__lte=week_end
        ).order_by('date')
        
        # Calculate weekly stats
        workout_completion = 0
        if week_workouts.count() > 0:
            completed_this_week = week_sessions.count()
            workout_completion = (completed_this_week / week_workouts.count()) * 100
        
        nutrition_adherence = 0
        if week_meals.count() > 0:
            logged_days = week_logs.count()
            nutrition_adherence = (logged_days / week_meals.count()) * 100
        
        # Get current progress
        progress = ProgressSyncService.update_user_progress(user)
        
        weekly_data = {
            'week_period': {
                'start': week_start.isoformat(),
                'end': week_end.isoformat(),
                'week_number': week_start.isocalendar()[1],
            },
            'workout_summary': {
                'planned_workouts': week_workouts.count(),
                'completed_workouts': week_sessions.count(),
                'completion_rate': round(workout_completion, 1),
                'total_calories_burned': sum(s.calories_burned for s in week_sessions),
                'total_duration': sum(
                    (s.end_time - s.start_time).total_seconds() / 60 
                    for s in week_sessions 
                    if s.end_time
                ),
                'workouts': [
                    {
                        'day': workout.day,
                        'type': workout.workout_type,
                        'duration': workout.estimated_duration,
                        'completed': workout.completed,
                        'rating': workout.user_rating,
                    }
                    for workout in week_workouts
                ]
            },
            'nutrition_summary': {
                'planned_meals': week_meals.count(),
                'logged_days': week_logs.count(),
                'adherence_rate': round(nutrition_adherence, 1),
                'total_calories_consumed': sum(log.total_calories for log in week_logs),
                'avg_daily_calories': week_logs.aggregate(
                    avg_calories=models.Avg('total_calories')
                )['avg_calories'] or 0 if week_logs.exists() else 0,
                'target_calories': user.healthmetrics.calculate_daily_calories(),
                'meals': [
                    {
                        'date': meal.date.isoformat(),
                        'calories': meal.total_calories,
                        'rating': meal.user_rating,
                    }
                    for meal in week_meals
                ]
            },
            'progress_highlights': {
                'current_streak': progress.workout_streak,
                'progress_score': progress.progress_score,
                'achievement_badges': progress.achievement_badges,
                'ai_insights': progress.ai_insights,
            }
        }
        
        return Response(weekly_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Failed to load weekly report', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_insights(request):
    """
    Get AI-powered progress insights and recommendations.
    
    This endpoint provides personalized insights based on the user's
    progress across all modules.
    """
    try:
        # Get updated progress
        progress = ProgressSyncService.update_user_progress(request.user)
        
        # Get additional context for insights
        health_metrics = request.user.healthmetrics
        
        # Get recent trends
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_sessions = WorkoutSession.objects.filter(
            user=request.user,
            start_time__gte=thirty_days_ago,
            completed=True
        ).order_by('start_time')
        
        recent_logs = NutritionLog.objects.filter(
            user=request.user,
            date__gte=thirty_days_ago.date()
        ).order_by('date')
        
        # Generate detailed insights
        insights_data = {
            'overall_progress': {
                'progress_score': progress.progress_score,
                'trend': 'improving' if progress.progress_score >= 70 else 'stable' if progress.progress_score >= 40 else 'needs_attention',
                'insights': progress.ai_insights,
            },
            'workout_insights': {
                'current_streak': progress.workout_streak,
                'total_workouts': progress.total_workouts,
                'recent_frequency': recent_sessions.count() / 4,  # workouts per week
                'recommendations': _generate_workout_recommendations(request.user, recent_sessions),
            },
            'nutrition_insights': {
                'adherence': progress.nutrition_adherence,
                'recent_logging': recent_logs.count() / 4,  # days logged per week
                'recommendations': _generate_nutrition_recommendations(request.user, recent_logs),
            },
            'goal_progress': {
                'current_weight': health_metrics.weight,
                'target_weight': health_metrics.target_weight,
                'weight_to_goal': abs(health_metrics.weight - health_metrics.target_weight) if health_metrics.target_weight else 0,
                'goal_achievement_probability': _calculate_goal_probability(request.user, progress),
            },
            'achievements': {
                'total_badges': len(progress.achievement_badges),
                'recent_badges': progress.achievement_badges[-3:],  # Last 3 badges
                'next_milestone': _get_next_milestone(progress),
            }
        }
        
        return Response(insights_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Failed to load progress insights', 'detail': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _generate_workout_recommendations(user, recent_sessions):
    """Generate workout-specific recommendations."""
    recommendations = []
    
    if not recent_sessions.exists():
        recommendations.append("Start with 2-3 workouts per week to build consistency.")
    else:
        frequency = recent_sessions.count() / 4  # per week
        if frequency < 2:
            recommendations.append("Try to exercise at least 2-3 times per week for better results.")
        elif frequency >= 4:
            recommendations.append("Great consistency! Consider varying your workout intensity.")
        
        # Check ratings
        avg_rating = recent_sessions.exclude(difficulty_rating__isnull=True).aggregate(
            avg_rating=models.Avg('difficulty_rating')
        )['avg_rating']
        
        if avg_rating and avg_rating <= 2:
            recommendations.append("Consider reducing workout intensity or trying different exercises.")
        elif avg_rating and avg_rating >= 4:
            recommendations.append("You're handling the intensity well! Ready to progress?")
    
    return recommendations


def _generate_nutrition_recommendations(user, recent_logs):
    """Generate nutrition-specific recommendations."""
    recommendations = []
    
    if not recent_logs.exists():
        recommendations.append("Start tracking your meals to monitor your nutrition intake.")
    else:
        adherence = recent_logs.count() / 4  # days logged per week
        if adherence < 5:
            recommendations.append("Try to log your meals consistently for better tracking.")
        
        # Check calorie consistency
        avg_calories = recent_logs.aggregate(avg_calories=models.Avg('total_calories'))['avg_calories']
        target_calories = user.healthmetrics.calculate_daily_calories()
        
        if avg_calories and target_calories:
            if abs(avg_calories - target_calories) > 300:
                recommendations.append("Focus on hitting your daily calorie target more consistently.")
        
        # Check protein intake
        avg_protein = recent_logs.aggregate(avg_protein=models.Avg('total_protein'))['avg_protein']
        if avg_protein and avg_protein < (user.healthmetrics.weight * 1.6):  # 1.6g per kg for active people
            recommendations.append("Consider increasing your protein intake for better muscle recovery.")
    
    return recommendations


def _calculate_goal_probability(user, progress):
    """Calculate probability of achieving fitness goal."""
    try:
        health_metrics = user.healthmetrics
        
        if not health_metrics.target_weight:
            return 0.7  # Default probability for maintenance goals
        
        # Simple calculation based on current progress score
        base_probability = progress.progress_score / 100
        
        # Adjust based on goal type
        if health_metrics.fitness_goal == 'weight_loss':
            return min(0.95, base_probability + 0.2)
        elif health_metrics.fitness_goal == 'muscle_gain':
            return min(0.9, base_probability + 0.15)
        else:
            return min(0.85, base_probability + 0.1)
    
    except:
        return 0.5


def _get_next_milestone(progress):
    """Get the next achievement milestone."""
    if progress.workout_streak < 7:
        return "7-Day Workout Streak"
    elif progress.workout_streak < 14:
        return "14-Day Workout Streak"
    elif progress.total_workouts < 50:
        return "50 Total Workouts"
    elif progress.progress_score < 80:
        return "80% Progress Score"
    else:
        return "Fitness Master"
