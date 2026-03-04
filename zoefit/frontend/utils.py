"""
Utility functions for frontend module.

This module contains helper functions and utilities that support
the frontend module operations. These functions handle common tasks
like data processing, calculations, and formatting.

Key utilities:
- Date and time helpers
- Progress calculations
- Streak management
- Data aggregation
- Export functions
- Achievement helpers
"""

from datetime import datetime, timedelta, date
from decimal import Decimal
from django.utils import timezone
from django.db.models import Avg, Count, Sum, Max, Min, Q
from django.contrib.auth import get_user_model

from .models import (
    WorkoutSession, ExerciseLog, ProgressSnapshot,
    Streak, MealLog, Achievement
)

User = get_user_model()


class DateRange:
    """Helper class for working with date ranges."""
    
    @staticmethod
    def get_period_dates(period):
        """Get start and end dates for a given period."""
        today = timezone.now().date()
        
        if period == 'today':
            return today, today
        elif period == 'yesterday':
            return today - timedelta(days=1), today - timedelta(days=1)
        elif period == 'week':
            start = today - timedelta(days=today.weekday())
            return start, today
        elif period == 'last_week':
            start = today - timedelta(days=today.weekday() + 7)
            end = start + timedelta(days=6)
            return start, end
        elif period == 'month':
            start = today.replace(day=1)
            return start, today
        elif period == 'last_month':
            if today.month == 1:
                start = today.replace(year=today.year - 1, month=12, day=1)
                end = today.replace(year=today.year - 1, month=12, day=31)
            else:
                start = today.replace(month=today.month - 1, day=1)
                # Get last day of previous month
                next_month = start.replace(month=start.month + 1) if start.month < 12 else start.replace(year=start.year + 1, month=1)
                end = next_month - timedelta(days=1)
            return start, end
        elif period == 'quarter':
            quarter = (today.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start = today.replace(month=start_month, day=1)
            return start, today
        elif period == 'year':
            start = today.replace(month=1, day=1)
            return start, today
        elif period == 'last_year':
            start = today.replace(year=today.year - 1, month=1, day=1)
            end = today.replace(year=today.year - 1, month=12, day=31)
            return start, end
        else:
            # Default to last 30 days
            return today - timedelta(days=30), today
    
    @staticmethod
    def get_week_range(week_offset=0):
        """Get start and end dates for a week with offset."""
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday()) - timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week
    
    @staticmethod
    def get_month_range(month_offset=0):
        """Get start and end dates for a month with offset."""
        today = timezone.now().date()
        if month_offset == 0:
            start = today.replace(day=1)
        else:
            # Calculate target month
            target_month = today.month - month_offset
            target_year = today.year
            
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            while target_month > 12:
                target_month -= 12
                target_year += 1
            
            start = today.replace(year=target_year, month=target_month, day=1)
        
        # Get end of month
        if start.month == 12:
            next_month = start.replace(year=start.year + 1, month=1, day=1)
        else:
            next_month = start.replace(month=start.month + 1, day=1)
        
        end = next_month - timedelta(days=1)
        return start, end


class ProgressCalculator:
    """Helper class for progress calculations."""
    
    @staticmethod
    def calculate_weight_change(user, start_date=None, end_date=None):
        """Calculate weight change over a period."""
        if not start_date or not end_date:
            start_date, end_date = DateRange.get_period_dates('month')
        
        snapshots = ProgressSnapshot.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date,
            weight__isnull=False
        ).order_by('date')
        
        if len(snapshots) < 2:
            return None, None, None
        
        start_weight = snapshots.first().weight
        end_weight = snapshots.last().weight
        change = end_weight - start_weight
        percentage_change = (change / start_weight) * 100 if start_weight > 0 else 0
        
        return change, percentage_change, snapshots.count()
    
    @staticmethod
    def calculate_body_composition_change(user, start_date=None, end_date=None):
        """Calculate body composition changes."""
        if not start_date or not end_date:
            start_date, end_date = DateRange.get_period_dates('month')
        
        snapshots = ProgressSnapshot.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        if len(snapshots) < 2:
            return {}
        
        first = snapshots.first()
        last = snapshots.last()
        
        changes = {}
        
        if first.body_fat_percentage and last.body_fat_percentage:
            changes['body_fat'] = {
                'change': last.body_fat_percentage - first.body_fat_percentage,
                'percentage_change': ((last.body_fat_percentage - first.body_fat_percentage) / first.body_fat_percentage) * 100
            }
        
        if first.muscle_mass and last.muscle_mass:
            changes['muscle_mass'] = {
                'change': last.muscle_mass - first.muscle_mass,
                'percentage_change': ((last.muscle_mass - first.muscle_mass) / first.muscle_mass) * 100
            }
        
        # Calculate measurement changes
        if first.measurements and last.measurements:
            measurement_changes = {}
            for key in first.measurements:
                if key in last.measurements:
                    first_val = first.measurements[key]
                    last_val = last.measurements[key]
                    measurement_changes[key] = {
                        'change': last_val - first_val,
                        'percentage_change': ((last_val - first_val) / first_val) * 100 if first_val > 0 else 0
                    }
            changes['measurements'] = measurement_changes
        
        return changes
    
    @staticmethod
    def calculate_strength_progression(user, exercise_name=None, weeks=12):
        """Calculate strength progression for exercises."""
        start_date = timezone.now().date() - timedelta(weeks=weeks)
        
        logs = ExerciseLog.objects.filter(
            workout_session__user=user,
            workout_session__start_time__date__gte=start_date,
            weight_used__isnull=False
        )
        
        if exercise_name:
            logs = logs.filter(exercise_name__icontains=exercise_name)
        
        # Group by exercise name and calculate progression
        exercise_progress = {}
        
        for log in logs:
            if log.exercise_name not in exercise_progress:
                exercise_progress[log.exercise_name] = []
            exercise_progress[log.exercise_name].append({
                'date': log.workout_session.start_time.date(),
                'weight': log.weight_used,
                'reps': log.reps_per_set[0] if log.reps_per_set else 0,
                'volume': log.weight_used * (log.reps_per_set[0] if log.reps_per_set else 0)
            })
        
        # Calculate progression for each exercise
        results = {}
        for exercise, data in exercise_progress.items():
            if len(data) >= 2:
                data.sort(key=lambda x: x['date'])
                first = data[0]
                last = data[-1]
                
                volume_progress = ((last['volume'] - first['volume']) / first['volume']) * 100 if first['volume'] > 0 else 0
                weight_progress = ((last['weight'] - first['weight']) / first['weight']) * 100 if first['weight'] > 0 else 0
                
                results[exercise] = {
                    'volume_progression': round(volume_progress, 1),
                    'weight_progression': round(weight_progress, 1),
                    'sessions': len(data),
                    'first_session': first['date'],
                    'last_session': last['date']
                }
        
        return results


class StreakManager:
    """Helper class for managing streaks."""
    
    @staticmethod
    def update_all_streaks(user):
        """Update all streaks for a user based on recent activity."""
        StreakManager.update_workout_streak(user)
        StreakManager.update_calorie_streak(user)
        StreakManager.update_water_streak(user)
        StreakManager.update_steps_streak(user)
        StreakManager.update_meal_plan_streak(user)
    
    @staticmethod
    def update_workout_streak(user):
        """Update workout streak."""
        today = timezone.now().date()
        
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
                streak.current_count += 1
                streak.last_activity_date = today
            elif streak.last_activity_date < today - timedelta(days=1):
                streak.current_count = 1
                streak.start_date = today
                streak.last_activity_date = today
            
            streak.longest_count = max(streak.longest_count, streak.current_count)
            streak.is_active = True
            streak.save()
        elif streak.last_activity_date < today - timedelta(days=1):
            # Streak broken
            streak.is_active = False
            streak.save()
    
    @staticmethod
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
            streak.is_active = True
            streak.save()
        elif streak.last_activity_date < today - timedelta(days=1):
            streak.is_active = False
            streak.save()
    
    @staticmethod
    def update_water_streak(user):
        """Update water intake streak (placeholder for future implementation)."""
        # This would be implemented when water tracking is added
        pass
    
    @staticmethod
    def update_steps_streak(user):
        """Update steps goal streak (placeholder for future implementation)."""
        # This would be implemented when steps tracking is added
        pass
    
    @staticmethod
    def update_meal_plan_streak(user):
        """Update meal plan adherence streak."""
        today = timezone.now().date()
        
        streak, created = Streak.objects.get_or_create(
            user=user,
            streak_type='meal_plan',
            defaults={
                'current_count': 0,
                'longest_count': 0,
                'last_activity_date': today,
                'start_date': today,
                'is_active': True
            }
        )
        
        # Check if user followed meal plan today
        # This would involve comparing logged meals with AI meal plans
        # For now, we'll use meal logging as a proxy
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
            streak.is_active = True
            streak.save()
        elif streak.last_activity_date < today - timedelta(days=1):
            streak.is_active = False
            streak.save()


class AchievementManager:
    """Helper class for managing achievements."""
    
    @staticmethod
    def check_workout_achievements(user):
        """Check and award workout-related achievements."""
        total_workouts = WorkoutSession.objects.filter(user=user).count()
        completed_workouts = WorkoutSession.objects.filter(user=user, completed=True).count()
        
        # Check for workout count achievements
        workout_milestones = [1, 5, 10, 25, 50, 100, 250, 500]
        for milestone in workout_milestones:
            if total_workouts >= milestone:
                AchievementManager.award_achievement(
                    user,
                    'workout_count',
                    f'Workout Warrior {milestone}',
                    f'Complete {milestone} workouts',
                    'trophy',
                    milestone * 10
                )
        
        # Check for completion streak achievements
        workout_streak = Streak.objects.filter(
            user=user, streak_type='workout', is_active=True
        ).first()
        
        if workout_streak:
            streak_milestones = [3, 7, 14, 30, 60, 90, 180, 365]
            for milestone in streak_milestones:
                if workout_streak.current_count >= milestone:
                    AchievementManager.award_achievement(
                        user,
                        'workout_streak',
                        f'Consistency Champion {milestone}',
                        f'Maintain a {milestone}-day workout streak',
                        'fire',
                        milestone * 20
                    )
    
    @staticmethod
    def check_progress_achievements(user):
        """Check and award progress-related achievements."""
        # Check for weight loss achievements
        snapshots = ProgressSnapshot.objects.filter(
            user=user, weight__isnull=False
        ).order_by('date')
        
        if len(snapshots) >= 2:
            first_weight = snapshots.first().weight
            last_weight = snapshots.last().weight
            weight_loss = first_weight - last_weight
            
            weight_loss_milestones = [5, 10, 20, 30, 50]  # in kg
            for milestone in weight_loss_milestones:
                if weight_loss >= milestone:
                    AchievementManager.award_achievement(
                        user,
                        'weight_loss',
                        f'Weight Loss {milestone}kg',
                        f'Lose {milestone}kg',
                        'scale',
                        milestone * 15
                    )
    
    @staticmethod
    def award_achievement(user, achievement_type, title, description, badge_icon, points):
        """Award an achievement to a user if not already awarded."""
        existing = Achievement.objects.filter(
            user=user,
            achievement_type=achievement_type,
            title=title
        ).exists()
        
        if not existing:
            Achievement.objects.create(
                user=user,
                achievement_type=achievement_type,
                title=title,
                description=description,
                badge_icon=badge_icon,
                points_awarded=points
            )
            return True
        return False


class DataExporter:
    """Helper class for exporting user data."""
    
    @staticmethod
    def export_workout_data(user, start_date=None, end_date=None, format='csv'):
        """Export workout data for a user."""
        if not start_date or not end_date:
            start_date, end_date = DateRange.get_period_dates('year')
        
        sessions = WorkoutSession.objects.filter(
            user=user,
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        ).select_related('workout_plan').prefetch_related('exercise_logs')
        
        data = []
        for session in sessions:
            row = {
                'date': session.start_time.date(),
                'start_time': session.start_time,
                'end_time': session.end_time,
                'duration_minutes': int(session.duration.total_seconds() / 60) if session.duration else None,
                'completed': session.completed,
                'calories_burned': session.calories_burned,
                'difficulty_rating': session.difficulty_rating,
                'workout_plan_day': session.workout_plan.day if session.workout_plan else None,
                'exercise_count': session.exercise_logs.count(),
                'notes': session.user_notes
            }
            data.append(row)
        
        return data
    
    @staticmethod
    def export_nutrition_data(user, start_date=None, end_date=None, format='csv'):
        """Export nutrition data for a user."""
        if not start_date or not end_date:
            start_date, end_date = DateRange.get_period_dates('year')
        
        meals = MealLog.objects.filter(
            user=user,
            meal_time__date__gte=start_date,
            meal_time__date__lte=end_date
        ).order_by('meal_time')
        
        data = []
        for meal in meals:
            row = {
                'date': meal.meal_time.date(),
                'meal_time': meal.meal_time,
                'meal_type': meal.get_meal_type_display(),
                'total_calories': meal.total_calories,
                'protein': meal.protein,
                'carbs': meal.carbs,
                'fat': meal.fat,
                'food_items_count': len(meal.food_items) if meal.food_items else 0,
                'notes': meal.notes
            }
            data.append(row)
        
        return data
    
    @staticmethod
    def export_progress_data(user, start_date=None, end_date=None, format='csv'):
        """Export progress data for a user."""
        if not start_date or not end_date:
            start_date, end_date = DateRange.get_period_dates('year')
        
        snapshots = ProgressSnapshot.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        data = []
        for snapshot in snapshots:
            row = {
                'date': snapshot.date,
                'weight': snapshot.weight,
                'body_fat_percentage': snapshot.body_fat_percentage,
                'muscle_mass': snapshot.muscle_mass,
                'measurement_count': len(snapshot.measurements) if snapshot.measurements else 0,
                'notes': snapshot.notes
            }
            
            # Add individual measurements
            if snapshot.measurements:
                for key, value in snapshot.measurements.items():
                    row[f'measurement_{key}'] = value
            
            data.append(row)
        
        return data


class AnalyticsHelper:
    """Helper class for analytics calculations."""
    
    @staticmethod
    def get_workout_frequency(user, weeks=4):
        """Calculate workout frequency over specified weeks."""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        workout_count = WorkoutSession.objects.filter(
            user=user,
            start_time__date__gte=start_date,
            start_time__date__lte=end_date
        ).count()
        
        return workout_count / weeks
    
    @staticmethod
    def get_nutrition_consistency(user, days=30):
        """Calculate nutrition logging consistency."""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        days_with_meals = MealLog.objects.filter(
            user=user,
            meal_time__date__gte=start_date,
            meal_time__date__lte=end_date
        ).values('meal_time__date').distinct().count()
        
        return (days_with_meals / days) * 100
    
    @staticmethod
    def get_most_productive_day(user):
        """Find the day of week with most workouts."""
        from django.db.models import Case, When, IntegerField
        
        workouts = WorkoutSession.objects.filter(user=user, completed=True)
        
        if not workouts.exists():
            return None
        
        day_counts = {}
        for workout in workouts:
            day_name = workout.start_time.strftime('%A')
            day_counts[day_name] = day_counts.get(day_name, 0) + 1
        
        return max(day_counts.items(), key=lambda x: x[1]) if day_counts else None
    
    @staticmethod
    def calculate_engagement_score(user):
        """Calculate overall engagement score (0-100)."""
        # Factors: workout consistency, nutrition logging, progress tracking
        workout_freq = AnalyticsHelper.get_workout_frequency(user, 4)
        nutrition_consistency = AnalyticsHelper.get_nutrition_consistency(user, 30)
        
        # Progress snapshots in last 30 days
        progress_snapshots = ProgressSnapshot.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Normalize scores (0-100)
        workout_score = min(workout_freq * 25, 100)  # 4 workouts/week = 100
        nutrition_score = nutrition_consistency
        progress_score = min(progress_snapshots * 20, 100)  # 5 snapshots/month = 100
        
        # Weighted average
        engagement_score = (workout_score * 0.5) + (nutrition_score * 0.3) + (progress_score * 0.2)
        
        return round(engagement_score, 1)
