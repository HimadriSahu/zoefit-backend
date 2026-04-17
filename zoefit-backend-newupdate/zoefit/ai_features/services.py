"""
Service layer for AI features to coordinate between workout and nutrition modules.

This service layer provides a clean interface for cross-module operations,
ensuring proper data synchronization and consistent business logic.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.db import transaction, models
from django.utils import timezone
from .models import HealthMetrics, ProgressTracking
from workout.models import WorkoutPlan, WorkoutSession, WorkoutProgress
from nutrition.models import MealPlan, NutritionLog, NutritionProgress


class ProgressSyncService:
    """
    Service to synchronize progress data across workout and nutrition modules.
    
    This service ensures that ProgressTracking is always up-to-date with
    the latest data from workout and nutrition modules.
    """
    
    @staticmethod
    def update_user_progress(user) -> ProgressTracking:
        """
        Update or create ProgressTracking with latest data from all modules.
        
        Args:
            user: The user whose progress to update
            
        Returns:
            ProgressTracking: Updated progress tracking instance
        """
        try:
            with transaction.atomic():
                # Get or create progress tracking
                progress, created = ProgressTracking.objects.get_or_create(
                    user=user,
                    defaults={
                        'created_at': timezone.now()
                    }
                )
                
                # Get latest health metrics
                health_metrics = user.healthmetrics
                
                # Update basic measurements
                progress.weight = health_metrics.weight
                progress.body_fat_percentage = getattr(health_metrics, 'body_fat_percentage', None)
                progress.muscle_mass = getattr(health_metrics, 'muscle_mass', None)
                
                # Get workout data
                workout_data = ProgressSyncService._get_workout_aggregates(user)
                progress.workout_streak = workout_data['streak']
                progress.total_workouts = workout_data['total']
                progress.calories_burned = workout_data['calories_burned']
                
                # Get nutrition data
                nutrition_data = ProgressSyncService._get_nutrition_aggregates(user)
                progress.nutrition_adherence = nutrition_data['adherence']
                
                # Calculate overall progress score
                progress.progress_score = ProgressSyncService._calculate_progress_score(
                    workout_data, nutrition_data, health_metrics
                )
                
                # Generate AI insights
                progress.ai_insights = ProgressSyncService._generate_insights(
                    user, workout_data, nutrition_data, health_metrics
                )
                
                # Update achievement badges
                progress.achievement_badges = ProgressSyncService._update_achievements(
                    user, workout_data, nutrition_data
                )
                
                progress.save()
                return progress
                
        except Exception as e:
            # Log error and return existing progress
            print(f"Error updating progress for user {user.username}: {e}")
            return ProgressTracking.objects.filter(user=user).first()
    
    @staticmethod
    def _get_workout_aggregates(user: Dict) -> Dict[str, Any]:
        """Get aggregated workout data for the user."""
        try:
            # Get workout progress
            workout_progress = WorkoutProgress.objects.filter(user=user).first()
            
            # Get recent workout sessions (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_sessions = WorkoutSession.objects.filter(
                user=user,
                start_time__gte=thirty_days_ago,
                completed=True
            )
            
            # Calculate current streak
            current_streak = ProgressSyncService._calculate_workout_streak(user)
            
            return {
                'streak': current_streak,
                'total': workout_progress.total_workouts if workout_progress else 0,
                'calories_burned': sum(session.calories_burned for session in recent_sessions),
                'recent_sessions': recent_sessions.count(),
                'avg_rating': recent_sessions.exclude(difficulty_rating__isnull=True).aggregate(
                    avg_rating=models.Avg('difficulty_rating')
                )['avg_rating'] or 0
            }
        except:
            return {
                'streak': 0,
                'total': 0,
                'calories_burned': 0,
                'recent_sessions': 0,
                'avg_rating': 0
            }
    
    @staticmethod
    def _get_nutrition_aggregates(user: Dict) -> Dict[str, Any]:
        """Get aggregated nutrition data for the user."""
        try:
            # Get nutrition progress
            nutrition_progress = NutritionProgress.objects.filter(user=user).first()
            
            # Get recent nutrition logs (last 7 days)
            seven_days_ago = timezone.now() - timedelta(days=7)
            recent_logs = NutritionLog.objects.filter(
                user=user,
                date__gte=seven_days_ago.date()
            )
            
            # Calculate adherence (how well user follows meal plans)
            meal_plans_this_week = MealPlan.objects.filter(
                user=user,
                date__gte=seven_days_ago.date()
            ).count()
            
            adherence = 0
            if meal_plans_this_week > 0:
                # Simple adherence calculation based on log completeness
                complete_logs = recent_logs.exclude(
                    total_calories=0
                ).count()
                adherence = (complete_logs / meal_plans_this_week) * 100
            
            return {
                'adherence': min(100, adherence),
                'avg_daily_calories': recent_logs.aggregate(
                    avg_calories=models.Avg('total_calories')
                )['avg_calories'] or 0,
                'days_logged': recent_logs.count(),
                'target_calories': user.healthmetrics.calculate_daily_calories()
            }
        except:
            return {
                'adherence': 0,
                'avg_daily_calories': 0,
                'days_logged': 0,
                'target_calories': 0
            }
    
    @staticmethod
    def _calculate_workout_streak(user: Dict) -> int:
        """Calculate current workout streak."""
        try:
            sessions = WorkoutSession.objects.filter(
                user=user,
                completed=True
            ).order_by('-start_time')
            
            if not sessions:
                return 0
            
            streak = 0
            current_date = timezone.now().date()
            
            for session in sessions:
                session_date = session.start_time.date()
                
                # If session is from today or yesterday
                if session_date >= current_date - timedelta(days=1):
                    streak += 1
                    current_date = session_date
                else:
                    break
            
            return streak
        except:
            return 0
    
    @staticmethod
    def _calculate_progress_score(workout_data: Dict, nutrition_data: Dict, health_metrics: HealthMetrics) -> float:
        """Calculate overall progress score (0-100)."""
        try:
            # Workout score (40% weight)
            workout_score = 0
            if workout_data['total'] > 0:
                consistency_score = min(100, (workout_data['recent_sessions'] / 7) * 100)  # Sessions per week
                streak_score = min(100, workout_data['streak'] * 10)  # Streak bonus
                workout_score = (consistency_score + streak_score) / 2
            
            # Nutrition score (40% weight)
            nutrition_score = nutrition_data['adherence']
            
            # Goal progress score (20% weight)
            goal_score = 50  # Default
            if health_metrics.target_weight and health_metrics.weight:
                weight_diff = abs(health_metrics.weight - health_metrics.target_weight)
                initial_diff = abs(health_metrics.weight - health_metrics.target_weight)
                if initial_diff > 0:
                    goal_progress = 1 - (weight_diff / initial_diff)
                    goal_score = max(0, min(100, goal_progress * 100))
            
            # Weighted average
            total_score = (workout_score * 0.4) + (nutrition_score * 0.4) + (goal_score * 0.2)
            return round(min(100, max(0, total_score)), 2)
            
        except:
            return 0.0
    
    @staticmethod
    def _generate_insights(user: Dict, workout_data: Dict, nutrition_data: Dict, health_metrics: HealthMetrics) -> str:
        """Generate AI insights based on progress data."""
        insights = []
        
        # Workout insights
        if workout_data['streak'] >= 7:
            insights.append(f"🔥 Amazing {workout_data['streak']}-day workout streak! Keep it up!")
        elif workout_data['streak'] >= 3:
            insights.append(f"💪 Great consistency with {workout_data['streak']}-day workout streak.")
        elif workout_data['recent_sessions'] < 2:
            insights.append("📅 Try to exercise at least 3 times per week for better results.")
        
        # Nutrition insights
        if nutrition_data['adherence'] >= 80:
            insights.append("🥗 Excellent nutrition adherence! You're fueling your body well.")
        elif nutrition_data['adherence'] >= 60:
            insights.append("👍 Good nutrition tracking. Stay consistent for better results.")
        elif nutrition_data['adherence'] < 40:
            insights.append("📝 Focus on logging your meals consistently to track progress.")
        
        # Goal-specific insights
        if health_metrics.fitness_goal == 'weight_loss':
            if health_metrics.target_weight and health_metrics.weight > health_metrics.target_weight:
                remaining = health_metrics.weight - health_metrics.target_weight
                insights.append(f"🎯 {remaining:.1f}kg to reach your target weight. Stay consistent!")
        elif health_metrics.fitness_goal == 'muscle_gain':
            insights.append("💪 Focus on progressive overload and adequate protein intake.")
        
        return " | ".join(insights[:3]) if insights else "Keep tracking your progress for personalized insights!"
    
    @staticmethod
    def _update_achievements(user: Dict, workout_data: Dict, nutrition_data: Dict) -> List[str]:
        """Update achievement badges based on progress."""
        badges = []
        
        # Workout achievements
        if workout_data['streak'] >= 30:
            badges.append("🏆 Workout Warrior - 30 Day Streak")
        elif workout_data['streak'] >= 14:
            badges.append("🥈 Two Week Warrior")
        elif workout_data['streak'] >= 7:
            badges.append("🥉 Week Warrior")
        
        if workout_data['total'] >= 100:
            badges.append("💯 Century Club - 100 Workouts")
        elif workout_data['total'] >= 50:
            badges.append("🌟 Half Century - 50 Workouts")
        elif workout_data['total'] >= 10:
            badges.append("🎯 Getting Started - 10 Workouts")
        
        # Nutrition achievements
        if nutrition_data['adherence'] >= 90:
            badges.append("🥗 Nutrition Master")
        elif nutrition_data['adherence'] >= 75:
            badges.append("👨‍🍳 Healthy Eater")
        
        # Consistency achievements
        if nutrition_data['days_logged'] >= 30:
            badges.append("📝 Logging Legend")
        elif nutrition_data['days_logged'] >= 7:
            badges.append("📅 Weekly Tracker")
        
        return badges


class UserDataAggregationService:
    """
    Service to provide aggregated user data across all modules.
    
    This service consolidates data from workout, nutrition, and AI features
    to provide a complete view of the user's fitness journey.
    """
    
    @staticmethod
    def get_user_dashboard_data(user: Dict) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a user.
        
        Args:
            user: The user to get data for
            
        Returns:
            Dict containing aggregated dashboard data
        """
        try:
            # Get health metrics
            health_metrics = user.healthmetrics
            
            # Get progress tracking (update if needed)
            progress = ProgressSyncService.update_user_progress(user)
            
            # Get recent workout plans
            recent_workouts = WorkoutPlan.objects.filter(
                user=user,
                day__lte=timezone.now().date()
            ).order_by('-day')[:5]
            
            # Get recent meal plans
            recent_meals = MealPlan.objects.filter(
                user=user,
                date__lte=timezone.now().date()
            ).order_by('-date')[:7]
            
            # Get upcoming workout
            upcoming_workout = WorkoutPlan.objects.filter(
                user=user,
                completed=False
            ).order_by('day').first()
            
            # Get today's meal plan
            today_meal = MealPlan.objects.filter(
                user=user,
                date=timezone.now().date()
            ).first()
            
            return {
                'user_profile': {
                    'username': user.username,
                    'email': user.email,
                    'join_date': user.date_joined,
                },
                'health_metrics': {
                    'weight': health_metrics.weight,
                    'bmi': health_metrics.bmi,
                    'bmi_category': health_metrics.get_bmi_category(),
                    'fitness_goal': health_metrics.fitness_goal,
                    'activity_level': health_metrics.activity_level,
                    'target_weight': health_metrics.target_weight,
                    'daily_calories': health_metrics.calculate_daily_calories(),
                },
                'progress_summary': {
                    'progress_score': progress.progress_score,
                    'workout_streak': progress.workout_streak,
                    'total_workouts': progress.total_workouts,
                    'nutrition_adherence': progress.nutrition_adherence,
                    'achievement_badges': progress.achievement_badges,
                    'ai_insights': progress.ai_insights,
                },
                'recent_activity': {
                    'recent_workouts': [
                        {
                            'day': workout.day,
                            'type': workout.workout_type,
                            'duration': workout.estimated_duration,
                            'completed': workout.completed,
                            'rating': workout.user_rating,
                        }
                        for workout in recent_workouts
                    ],
                    'recent_meals': [
                        {
                            'date': meal.date,
                            'calories': meal.total_calories,
                            'rating': meal.user_rating,
                        }
                        for meal in recent_meals
                    ],
                },
                'upcoming': {
                    'next_workout': {
                        'day': upcoming_workout.day,
                        'type': upcoming_workout.workout_type,
                        'duration': upcoming_workout.estimated_duration,
                        'difficulty': upcoming_workout.difficulty_level,
                    } if upcoming_workout else None,
                    'today_meal': {
                        'date': today_meal.date,
                        'calories': today_meal.total_calories,
                        'meals': today_meal.meals,
                    } if today_meal else None,
                }
            }
            
        except Exception as e:
            print(f"Error getting dashboard data for user {user.username}: {e}")
            return {
                'error': 'Unable to load dashboard data',
                'user_profile': {'username': user.username},
            }
    
    @staticmethod
    def get_user_summary_stats(user: Dict) -> Dict[str, Any]:
        """Get summary statistics for a user."""
        try:
            # Get basic counts
            total_workouts = WorkoutPlan.objects.filter(user=user).count()
            completed_workouts = WorkoutPlan.objects.filter(user=user, completed=True).count()
            total_meal_plans = MealPlan.objects.filter(user=user).count()
            
            # Get current progress
            progress = ProgressSyncService.update_user_progress(user)
            
            # Get health metrics
            health_metrics = user.healthmetrics
            
            return {
                'workouts': {
                    'total': total_workouts,
                    'completed': completed_workouts,
                    'completion_rate': (completed_workouts / total_workouts * 100) if total_workouts > 0 else 0,
                    'current_streak': progress.workout_streak,
                },
                'nutrition': {
                    'total_meal_plans': total_meal_plans,
                    'adherence': progress.nutrition_adherence,
                    'target_calories': health_metrics.calculate_daily_calories(),
                },
                'progress': {
                    'overall_score': progress.progress_score,
                    'current_weight': health_metrics.weight,
                    'target_weight': health_metrics.target_weight,
                    'weight_to_goal': abs(health_metrics.weight - health_metrics.target_weight) if health_metrics.target_weight else 0,
                    'bmi_category': health_metrics.get_bmi_category(),
                },
                'achievements': {
                    'total_badges': len(progress.achievement_badges),
                    'badges': progress.achievement_badges,
                }
            }
            
        except Exception as e:
            print(f"Error getting summary stats for user {user.username}: {e}")
            return {'error': 'Unable to load summary statistics'}
