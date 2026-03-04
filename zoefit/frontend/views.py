"""
Frontend API views for ZoeFit

This module contains all the API endpoints that power the user-facing
features of ZoeFit. These views handle workout history, progress tracking,
streak management, meal logging, and dashboard functionality.

Key features:
- Workout session management and history
- Progress tracking and visualization data
- Streak tracking and analytics
- Meal logging and nutrition summaries
- Dashboard aggregation and insights
- Achievement system integration

All endpoints require JWT authentication and provide comprehensive
data for powering the ZoeFit web and mobile applications.
"""

from datetime import datetime, timedelta, date
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Q, F, Max, Min
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import (
    WorkoutSession, ExerciseLog, ProgressSnapshot,
    Streak, MealLog, Achievement
)
from .serializers import (
    WorkoutSessionSerializer, ExerciseLogSerializer,
    ProgressSnapshotSerializer, StreakSerializer,
    MealLogSerializer, AchievementSerializer,
    DashboardSummarySerializer, WorkoutStatsSerializer,
    NutritionSummarySerializer, ProgressChartSerializer
)


# Pagination classes
class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API responses."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class SmallResultsSetPagination(PageNumberPagination):
    """Smaller pagination for summary data."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# Workout History Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def workout_sessions_view(request):
    """
    Handle workout session listing and creation.
    
    GET: Get paginated list of user's workout sessions
    POST: Create a new workout session
    """
    if request.method == 'GET':
        # Query parameters for filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        completed = request.GET.get('completed')
        
        sessions = WorkoutSession.objects.filter(user=request.user)
        
        # Apply filters
        if start_date:
            sessions = sessions.filter(start_time__date__gte=start_date)
        if end_date:
            sessions = sessions.filter(start_time__date__lte=end_date)
        if completed:
            sessions = sessions.filter(completed=completed.lower() == 'true')
        
        # Order by most recent
        sessions = sessions.order_by('-start_time')
        
        # Paginate results
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(sessions, request)
        serializer = WorkoutSessionSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        # Create new workout session
        serializer = WorkoutSessionSerializer(data=request.data)
        if serializer.is_valid():
            session = serializer.save(user=request.user)
            
            # Update workout streak
            update_workout_streak(request.user)
            
            return Response(
                WorkoutSessionSerializer(session).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def workout_session_detail_view(request, session_id):
    """
    Handle individual workout session operations.
    
    GET: Get specific workout session details
    PUT: Update workout session
    DELETE: Delete workout session
    """
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    
    if request.method == 'GET':
        serializer = WorkoutSessionSerializer(session)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = WorkoutSessionSerializer(session, data=request.data, partial=True)
        if serializer.is_valid():
            updated_session = serializer.save()
            
            # Update streak if completion status changed
            if 'completed' in request.data:
                update_workout_streak(request.user)
            
            return Response(WorkoutSessionSerializer(updated_session).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        session.delete()
        return Response(
            {'message': 'Workout session deleted successfully'},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workout_stats_view(request):
    """
    Get comprehensive workout statistics for the user.
    
    Provides aggregated data including total workouts, duration,
    calories burned, completion rates, and progress metrics.
    """
    user = request.user
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Basic workout stats
    total_workouts = WorkoutSession.objects.filter(user=user).count()
    completed_workouts = WorkoutSession.objects.filter(user=user, completed=True).count()
    
    # Duration and calories
    workout_data = WorkoutSession.objects.filter(user=user).aggregate(
        total_duration=Sum('duration'),
        total_calories=Sum('calories_burned'),
        avg_duration=Avg('duration')
    )
    
    # Recent period stats (last 30 days)
    recent_workouts = WorkoutSession.objects.filter(
        user=user,
        start_time__date__gte=thirty_days_ago
    )
    
    # Most common exercise
    exercise_counts = ExerciseLog.objects.filter(
        workout_session__user=user
    ).values('exercise_name').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    # Workout frequency (per week)
    weeks_count = max(1, (today - thirty_days_ago).days // 7)
    workout_frequency = recent_workouts.count() / weeks_count
    
    # Calculate completion rate
    completion_rate = (completed_workouts / total_workouts * 100) if total_workouts > 0 else 0
    
    # Strength progress (based on weight progression in common exercises)
    strength_progress = calculate_strength_progress(user)
    
    # Cardio progress (based on duration/endurance improvement)
    cardio_progress = calculate_cardio_progress(user)
    
    stats_data = {
        'total_workouts': total_workouts,
        'total_duration_minutes': int(workout_data['total_duration'].total_seconds() / 60) if workout_data['total_duration'] else 0,
        'total_calories_burned': workout_data['total_calories'] or 0,
        'average_workout_duration': workout_data['avg_duration'].total_seconds() / 60 if workout_data['avg_duration'] else 0,
        'most_common_exercise': exercise_counts['exercise_name'] if exercise_counts else 'None',
        'workout_frequency': round(workout_frequency, 1),
        'completion_rate': round(completion_rate, 1),
        'strength_progress': strength_progress,
        'cardio_progress': cardio_progress
    }
    
    serializer = WorkoutStatsSerializer(stats_data)
    return Response(serializer.data)


# Progress Tracking Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def progress_snapshots_view(request):
    """
    Handle progress snapshot listing and creation.
    
    GET: Get user's progress snapshots
    POST: Create new progress snapshot
    """
    if request.method == 'GET':
        # Query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        snapshots = ProgressSnapshot.objects.filter(user=request.user)
        
        if start_date:
            snapshots = snapshots.filter(date__gte=start_date)
        if end_date:
            snapshots = snapshots.filter(date__lte=end_date)
        
        snapshots = snapshots.order_by('-date')
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(snapshots, request)
        serializer = ProgressSnapshotSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProgressSnapshotSerializer(data=request.data)
        if serializer.is_valid():
            snapshot = serializer.save(user=request.user)
            return Response(
                ProgressSnapshotSerializer(snapshot).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_charts_view(request):
    """
    Get progress data formatted for charts.
    
    Returns data for weight trends, body composition changes,
    and measurement progress over specified time periods.
    """
    user = request.user
    chart_type = request.GET.get('chart_type', 'weight')
    period = request.GET.get('period', 'month')
    
    # Calculate date range based on period
    end_date = timezone.now().date()
    if period == 'week':
        start_date = end_date - timedelta(weeks=12)
    elif period == 'month':
        start_date = end_date - timedelta(days=365)
    elif period == 'quarter':
        start_date = end_date - timedelta(days=730)
    else:  # year
        start_date = end_date - timedelta(days=3650)  # 10 years
    
    snapshots = ProgressSnapshot.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Format data points based on chart type
    data_points = []
    for snapshot in snapshots:
        point = {'date': snapshot.date.isoformat()}
        
        if chart_type == 'weight' and snapshot.weight:
            point['value'] = snapshot.weight
        elif chart_type == 'body_fat' and snapshot.body_fat_percentage:
            point['value'] = snapshot.body_fat_percentage
        elif chart_type == 'muscle_mass' and snapshot.muscle_mass:
            point['value'] = snapshot.muscle_mass
        elif chart_type == 'measurements' and snapshot.measurements:
            point.update(snapshot.measurements)
        
        if 'value' in point or chart_type == 'measurements':
            data_points.append(point)
    
    # Calculate trend
    trend = calculate_trend(data_points, chart_type)
    change_percentage = calculate_change_percentage(data_points, chart_type)
    
    chart_data = {
        'chart_type': chart_type,
        'data_points': data_points,
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'trend': trend,
        'change_percentage': change_percentage
    }
    
    serializer = ProgressChartSerializer(chart_data)
    return Response(serializer.data)


# Streak Tracking Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def streaks_view(request):
    """
    Get user's current streaks.
    
    Returns all active streaks including workout, calorie logging,
    water intake, and steps goal streaks.
    """
    streaks = Streak.objects.filter(user=request.user, is_active=True)
    serializer = StreakSerializer(streaks, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def streak_history_view(request):
    """
    Get streak history and analytics.
    
    Provides historical streak data, patterns, and insights
    for user motivation and progress tracking.
    """
    user = request.user
    streak_type = request.GET.get('streak_type')
    
    streaks = Streak.objects.filter(user=user)
    if streak_type:
        streaks = streaks.filter(streak_type=streak_type)
    
    streaks = streaks.order_by('-updated_at')
    
    # Calculate streak analytics
    analytics = {
        'total_streaks_earned': streaks.count(),
        'current_longest_streak': streaks.filter(is_active=True).aggregate(
            max_count=Max('current_count')
        )['max_count'] or 0,
        'all_time_longest_streak': streaks.aggregate(
            max_count=Max('longest_count')
        )['max_count'] or 0,
        'streak_history': StreakSerializer(streaks, many=True).data
    }
    
    return Response(analytics)


# Meal Logging Views
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def meal_logs_view(request):
    """
    Handle meal log listing and creation.
    
    GET: Get user's meal logs with filtering
    POST: Log a new meal
    """
    if request.method == 'GET':
        # Query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        meal_type = request.GET.get('meal_type')
        
        meals = MealLog.objects.filter(user=request.user)
        
        if start_date:
            meals = meals.filter(meal_time__date__gte=start_date)
        if end_date:
            meals = meals.filter(meal_time__date__lte=end_date)
        if meal_type:
            meals = meals.filter(meal_type=meal_type)
        
        meals = meals.order_by('-meal_time')
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(meals, request)
        serializer = MealLogSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = MealLogSerializer(data=request.data)
        if serializer.is_valid():
            meal = serializer.save(user=request.user)
            
            # Update calorie logging streak
            update_calorie_streak(request.user)
            
            return Response(
                MealLogSerializer(meal).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def nutrition_summary_view(request):
    """
    Get nutrition summary and analytics.
    
    Provides aggregated nutrition data for daily, weekly,
    and monthly periods with consistency tracking.
    """
    user = request.user
    period = request.GET.get('period', 'weekly')
    today = timezone.now().date()
    
    # Calculate date range based on period
    if period == 'daily':
        start_date = today
        end_date = today
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == 'monthly':
        start_date = today - timedelta(days=30)
        end_date = today
    else:  # yearly
        start_date = today - timedelta(days=365)
        end_date = today
    
    # Get meal logs for the period
    meals = MealLog.objects.filter(
        user=user,
        meal_time__date__gte=start_date,
        meal_time__date__lte=end_date
    )
    
    # Aggregate nutrition data
    nutrition_data = meals.aggregate(
        total_calories=Sum('total_calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbs'),
        total_fat=Sum('fat'),
        meals_count=Count('id')
    )
    
    # Calculate average daily calories
    days_count = (end_date - start_date).days + 1
    average_daily_calories = (nutrition_data['total_calories'] or 0) / days_count
    
    # Calculate macro percentages
    total_macros = (nutrition_data['total_protein'] or 0) * 4 + \
                   (nutrition_data['total_carbs'] or 0) * 4 + \
                   (nutrition_data['total_fat'] or 0) * 9
    
    average_macros = {}
    if total_macros > 0:
        average_macros = {
            'protein': round(((nutrition_data['total_protein'] or 0) * 4 / total_macros) * 100, 1),
            'carbs': round(((nutrition_data['total_carbs'] or 0) * 4 / total_macros) * 100, 1),
            'fat': round(((nutrition_data['total_fat'] or 0) * 9 / total_macros) * 100, 1)
        }
    
    # Calculate nutrition consistency
    days_with_meals = meals.values('meal_time__date').distinct().count()
    nutrition_consistency = (days_with_meals / days_count) * 100 if days_count > 0 else 0
    
    summary_data = {
        'period': period,
        'total_calories': nutrition_data['total_calories'] or 0,
        'average_daily_calories': round(average_daily_calories, 1),
        'total_protein': nutrition_data['total_protein'] or 0,
        'total_carbs': nutrition_data['total_carbs'] or 0,
        'total_fat': nutrition_data['total_fat'] or 0,
        'average_macros': average_macros,
        'meals_logged': nutrition_data['meals_count'] or 0,
        'nutrition_consistency': round(nutrition_consistency, 1)
    }
    
    serializer = NutritionSummarySerializer(summary_data)
    return Response(serializer.data)


# Dashboard Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary_view(request):
    """
    Get comprehensive dashboard summary.
    
    Aggregates data from all modules to provide a complete
    overview of user's fitness status and recent activity.
    """
    user = request.user
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Workout data
    total_workouts = WorkoutSession.objects.filter(user=user).count()
    recent_workouts = WorkoutSession.objects.filter(
        user=user,
        start_time__date__gte=thirty_days_ago
    ).order_by('-start_time')[:5]
    
    # Streak data
    workout_streak = Streak.objects.filter(
        user=user, streak_type='workout', is_active=True
    ).first()
    
    current_workout_streak = workout_streak.current_count if workout_streak else 0
    longest_workout_streak = workout_streak.longest_count if workout_streak else 0
    
    # Calories data
    total_calories_burned = WorkoutSession.objects.filter(
        user=user
    ).aggregate(total=Sum('calories_burned'))['total'] or 0
    
    # Progress data
    latest_snapshot = ProgressSnapshot.objects.filter(user=user).last()
    previous_snapshot = ProgressSnapshot.objects.filter(
        user=user,
        date__lt=latest_snapshot.date if latest_snapshot else today
    ).last()
    
    current_weight = latest_snapshot.weight if latest_snapshot else None
    weight_change = None
    
    if current_weight and previous_snapshot and previous_snapshot.weight:
        weight_change = current_weight - previous_snapshot.weight
    
    # Meal data
    meals_logged_today = MealLog.objects.filter(
        user=user,
        meal_time__date=today
    ).count()
    
    # Achievement data
    active_achievements = Achievement.objects.filter(
        user=user,
        is_displayed=True
    ).count()
    
    total_points = Achievement.objects.filter(
        user=user
    ).aggregate(total=Sum('points_awarded'))['total'] or 0
    
    recent_achievements = Achievement.objects.filter(
        user=user
    ).order_by('-earned_date')[:5]
    
    # Active streaks
    active_streaks = Streak.objects.filter(user=user, is_active=True)
    
    dashboard_data = {
        'total_workouts': total_workouts,
        'current_workout_streak': current_workout_streak,
        'longest_workout_streak': longest_workout_streak,
        'total_calories_burned': total_calories_burned,
        'current_weight': current_weight,
        'weight_change': weight_change,
        'meals_logged_today': meals_logged_today,
        'active_achievements': active_achievements,
        'total_points': total_points,
        'recent_workouts': WorkoutSessionSerializer(recent_workouts, many=True).data,
        'active_streaks': StreakSerializer(active_streaks, many=True).data,
        'recent_achievements': AchievementSerializer(recent_achievements, many=True).data
    }
    
    serializer = DashboardSummarySerializer(dashboard_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def achievements_view(request):
    """
    Get user's achievements and milestones.
    
    Returns all achievements earned by the user with
    filtering options for display and analytics.
    """
    user = request.user
    is_displayed = request.GET.get('displayed')
    
    achievements = Achievement.objects.filter(user=user)
    
    if is_displayed is not None:
        achievements = achievements.filter(is_displayed=is_displayed.lower() == 'true')
    
    achievements = achievements.order_by('-earned_date')
    
    paginator = SmallResultsSetPagination()
    result_page = paginator.paginate_queryset(achievements, request)
    serializer = AchievementSerializer(result_page, many=True)
    
    return paginator.get_paginated_response(serializer.data)


# Helper functions
def update_workout_streak(user):
    """Update workout streak based on recent activity."""
    today = timezone.now().date()
    
    # Get or create workout streak
    streak, created = Streak.objects.get_or_create(
        user=user,
        streak_type='workout',
        defaults={
            'current_count': 0,
            'longest_count': 0,
            'last_activity_date': today,
            'start_date': today,
            'is_active': True
        }
    )
    
    # Check if user worked out today
    worked_out_today = WorkoutSession.objects.filter(
        user=user,
        start_time__date=today
    ).exists()
    
    if worked_out_today:
        if streak.last_activity_date == today - timedelta(days=1):
            # Continue streak
            streak.current_count += 1
            streak.last_activity_date = today
        elif streak.last_activity_date < today - timedelta(days=1):
            # Reset streak
            streak.current_count = 1
            streak.start_date = today
            streak.last_activity_date = today
        # Update longest count
        streak.longest_count = max(streak.longest_count, streak.current_count)
        streak.save()


def update_calorie_streak(user):
    """Update calorie logging streak."""
    today = timezone.now().date()
    
    streak, created = Streak.objects.get_or_create(
        user=user,
        streak_type='calorie',
        defaults={
            'current_count': 0,
            'longest_count': 0,
            'last_activity_date': today,
            'start_date': today,
            'is_active': True
        }
    )
    
    logged_today = MealLog.objects.filter(
        user=user,
        meal_time__date=today
    ).exists()
    
    if logged_today:
        if streak.last_activity_date == today - timedelta(days=1):
            streak.current_count += 1
            streak.last_activity_date = today
        elif streak.last_activity_date < today - timedelta(days=1):
            streak.current_count = 1
            streak.start_date = today
            streak.last_activity_date = today
        
        streak.longest_count = max(streak.longest_count, streak.current_count)
        streak.save()


def calculate_strength_progress(user):
    """Calculate strength progress based on weight progression."""
    # This is a simplified calculation - in production, you'd want
    # more sophisticated analysis of strength progression
    recent_exercises = ExerciseLog.objects.filter(
        workout_session__user=user,
        weight_used__isnull=False
    ).order_by('-workout_session__start_time')[:20]
    
    older_exercises = ExerciseLog.objects.filter(
        workout_session__user=user,
        weight_used__isnull=False
    ).order_by('workout_session__start_time')[:20]
    
    if not recent_exercises or not older_exercises:
        return None
    
    recent_avg = sum(ex.weight_used or 0 for ex in recent_exercises) / len(recent_exercises)
    older_avg = sum(ex.weight_used or 0 for ex in older_exercises) / len(older_exercises)
    
    if older_avg == 0:
        return None
    
    progress = ((recent_avg - older_avg) / older_avg) * 100
    return round(progress, 1)


def calculate_cardio_progress(user):
    """Calculate cardio progress based on duration/endurance."""
    recent_sessions = WorkoutSession.objects.filter(
        user=user,
        completed=True
    ).order_by('-start_time')[:10]
    
    older_sessions = WorkoutSession.objects.filter(
        user=user,
        completed=True
    ).order_by('start_time')[:10]
    
    if not recent_sessions or not older_sessions:
        return None
    
    recent_avg = sum(s.duration.total_seconds() / 60 for s in recent_sessions if s.duration) / len(recent_sessions)
    older_avg = sum(s.duration.total_seconds() / 60 for s in older_sessions if s.duration) / len(older_sessions)
    
    if older_avg == 0:
        return None
    
    progress = ((recent_avg - older_avg) / older_avg) * 100
    return round(progress, 1)


def calculate_trend(data_points, chart_type):
    """Calculate trend direction for chart data."""
    if len(data_points) < 2:
        return 'stable'
    
    if chart_type == 'measurements':
        return 'stable'  # Complex calculations needed for multiple measurements
    
    # Simple trend calculation
    recent_values = [point.get('value', 0) for point in data_points[-5:]]
    older_values = [point.get('value', 0) for point in data_points[:5]]
    
    recent_avg = sum(recent_values) / len(recent_values) if recent_values else 0
    older_avg = sum(older_values) / len(older_values) if older_values else 0
    
    if recent_avg > older_avg * 1.05:
        return 'increasing'
    elif recent_avg < older_avg * 0.95:
        return 'decreasing'
    else:
        return 'stable'


def calculate_change_percentage(data_points, chart_type):
    """Calculate percentage change over the period."""
    if len(data_points) < 2 or chart_type == 'measurements':
        return None
    
    first_value = data_points[0].get('value', 0)
    last_value = data_points[-1].get('value', 0)
    
    if first_value == 0:
        return None
    
    change = ((last_value - first_value) / first_value) * 100
    return round(change, 1)
