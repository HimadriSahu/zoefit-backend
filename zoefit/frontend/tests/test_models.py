"""
Test cases for frontend module models.

This module contains unit tests for all frontend models to ensure
data integrity, validation, and proper functionality.

Tests cover:
- Model creation and validation
- Field constraints and relationships
- Model methods and properties
- Database constraints
- Edge cases and error conditions
"""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from frontend.models import (
    WorkoutSession, ExerciseLog, ProgressSnapshot,
    Streak, MealLog, Achievement
)

User = get_user_model()


class WorkoutSessionModelTest(TestCase):
    """Test cases for WorkoutSession model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_workout_session_creation(self):
        """Test basic workout session creation."""
        session = WorkoutSession.objects.create(
            user=self.user,
            start_time=timezone.now(),
            completed=True,
            calories_burned=500
        )
        
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.completed)
        self.assertEqual(session.calories_burned, 500)
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.updated_at)
    
    def test_workout_session_duration_calculation(self):
        """Test automatic duration calculation."""
        start_time = timezone.now() - timedelta(hours=1)
        end_time = timezone.now()
        
        session = WorkoutSession.objects.create(
            user=self.user,
            start_time=start_time,
            end_time=end_time,
            completed=True
        )
        
        session.save()  # Trigger duration calculation
        
        self.assertIsNotNone(session.duration)
        self.assertEqual(session.duration, end_time - start_time)
    
    def test_workout_session_string_representation(self):
        """Test string representation of workout session."""
        start_time = timezone.now()
        session = WorkoutSession.objects.create(
            user=self.user,
            start_time=start_time,
            completed=True
        )
        
        expected = f"{self.user.username}'s Workout - {start_time.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(session), expected)
    
    def test_workout_session_negative_calories_validation(self):
        """Test that negative calories are rejected."""
        with self.assertRaises(Exception):
            session = WorkoutSession(
                user=self.user,
                start_time=timezone.now(),
                calories_burned=-100
            )
            session.full_clean()


class ExerciseLogModelTest(TestCase):
    """Test cases for ExerciseLog model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.workout_session = WorkoutSession.objects.create(
            user=self.user,
            start_time=timezone.now(),
            completed=True
        )
    
    def test_exercise_log_creation(self):
        """Test basic exercise log creation."""
        log = ExerciseLog.objects.create(
            workout_session=self.workout_session,
            exercise_name='Bench Press',
            sets_completed=3,
            reps_per_set=[10, 8, 6],
            weight_used=50.0
        )
        
        self.assertEqual(log.workout_session, self.workout_session)
        self.assertEqual(log.exercise_name, 'Bench Press')
        self.assertEqual(log.sets_completed, 3)
        self.assertEqual(log.reps_per_set, [10, 8, 6])
        self.assertEqual(log.weight_used, 50.0)
    
    def test_exercise_log_string_representation(self):
        """Test string representation of exercise log."""
        log = ExerciseLog.objects.create(
            workout_session=self.workout_session,
            exercise_name='Squat',
            sets_completed=4,
            reps_per_set=[12, 10, 8, 6]
        )
        
        expected = f"Squat - {self.workout_session}"
        self.assertEqual(str(log), expected)


class ProgressSnapshotModelTest(TestCase):
    """Test cases for ProgressSnapshot model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_progress_snapshot_creation(self):
        """Test basic progress snapshot creation."""
        snapshot = ProgressSnapshot.objects.create(
            user=self.user,
            date=timezone.now().date(),
            weight=75.5,
            body_fat_percentage=15.0,
            measurements={'chest': 95, 'waist': 80, 'arms': 35}
        )
        
        self.assertEqual(snapshot.user, self.user)
        self.assertEqual(snapshot.weight, 75.5)
        self.assertEqual(snapshot.body_fat_percentage, 15.0)
        self.assertEqual(snapshot.measurements['chest'], 95)
    
    def test_progress_snapshot_unique_date_constraint(self):
        """Test that snapshots have unique dates per user."""
        date = timezone.now().date()
        
        ProgressSnapshot.objects.create(
            user=self.user,
            date=date,
            weight=75.0
        )
        
        # Attempting to create another snapshot for the same date should fail
        with self.assertRaises(Exception):
            ProgressSnapshot.objects.create(
                user=self.user,
                date=date,
                weight=76.0
            )
    
    def test_progress_snapshot_string_representation(self):
        """Test string representation of progress snapshot."""
        date = timezone.now().date()
        snapshot = ProgressSnapshot.objects.create(
            user=self.user,
            date=date,
            weight=75.0
        )
        
        expected = f"{self.user.username}'s Progress - {date}"
        self.assertEqual(str(snapshot), expected)


class StreakModelTest(TestCase):
    """Test cases for Streak model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_streak_creation(self):
        """Test basic streak creation."""
        today = timezone.now().date()
        streak = Streak.objects.create(
            user=self.user,
            streak_type='workout',
            current_count=5,
            longest_count=10,
            last_activity_date=today,
            start_date=today - timedelta(days=4)
        )
        
        self.assertEqual(streak.user, self.user)
        self.assertEqual(streak.streak_type, 'workout')
        self.assertEqual(streak.current_count, 5)
        self.assertEqual(streak.longest_count, 10)
        self.assertTrue(streak.is_active)
    
    def test_streak_unique_type_constraint(self):
        """Test that streak types are unique per user."""
        Streak.objects.create(
            user=self.user,
            streak_type='workout',
            current_count=1,
            last_activity_date=timezone.now().date(),
            start_date=timezone.now().date()
        )
        
        # Attempting to create another workout streak should fail
        with self.assertRaises(Exception):
            Streak.objects.create(
                user=self.user,
                streak_type='workout',
                current_count=2,
                last_activity_date=timezone.now().date(),
                start_date=timezone.now().date()
            )
    
    def test_streak_string_representation(self):
        """Test string representation of streak."""
        streak = Streak.objects.create(
            user=self.user,
            streak_type='workout',
            current_count=7,
            last_activity_date=timezone.now().date(),
            start_date=timezone.now().date() - timedelta(days=6)
        )
        
        expected = f"{self.user.username}'s Workout Streak - 7 days"
        self.assertEqual(str(streak), expected)


class MealLogModelTest(TestCase):
    """Test cases for MealLog model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_meal_log_creation(self):
        """Test basic meal log creation."""
        food_items = [
            {'name': 'Chicken Breast', 'quantity': '200g', 'calories': 330},
            {'name': 'Rice', 'quantity': '150g', 'calories': 200}
        ]
        
        meal = MealLog.objects.create(
            user=self.user,
            meal_type='lunch',
            food_items=food_items,
            total_calories=530,
            protein=40.0,
            carbs=45.0,
            fat=8.0,
            meal_time=timezone.now()
        )
        
        self.assertEqual(meal.user, self.user)
        self.assertEqual(meal.meal_type, 'lunch')
        self.assertEqual(len(meal.food_items), 2)
        self.assertEqual(meal.total_calories, 530)
        self.assertEqual(meal.protein, 40.0)
    
    def test_meal_log_string_representation(self):
        """Test string representation of meal log."""
        meal_time = timezone.now()
        meal = MealLog.objects.create(
            user=self.user,
            meal_type='breakfast',
            food_items=[{'name': 'Oatmeal', 'quantity': '1 bowl', 'calories': 150}],
            total_calories=150,
            meal_time=meal_time
        )
        
        expected = f"{self.user.username}'s Breakfast - {meal_time.strftime('%Y-%m-%d %H:%M')}"
        self.assertEqual(str(meal), expected)


class AchievementModelTest(TestCase):
    """Test cases for Achievement model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_achievement_creation(self):
        """Test basic achievement creation."""
        achievement = Achievement.objects.create(
            user=self.user,
            achievement_type='workout_count',
            title='Workout Warrior 10',
            description='Complete 10 workouts',
            badge_icon='trophy',
            points_awarded=100
        )
        
        self.assertEqual(achievement.user, self.user)
        self.assertEqual(achievement.achievement_type, 'workout_count')
        self.assertEqual(achievement.title, 'Workout Warrior 10')
        self.assertEqual(achievement.points_awarded, 100)
        self.assertTrue(achievement.is_displayed)
        self.assertIsNotNone(achievement.earned_date)
    
    def test_achievement_string_representation(self):
        """Test string representation of achievement."""
        achievement = Achievement.objects.create(
            user=self.user,
            achievement_type='weight_loss',
            title='Weight Loss 5kg',
            description='Lose 5kg',
            badge_icon='scale',
            points_awarded=75
        )
        
        expected = f"{self.user.username} - Weight Loss 5kg"
        self.assertEqual(str(achievement), expected)


class ModelRelationshipsTest(TestCase):
    """Test cases for model relationships and cascading behavior."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_workout_session_exercise_logs_relationship(self):
        """Test relationship between workout sessions and exercise logs."""
        session = WorkoutSession.objects.create(
            user=self.user,
            start_time=timezone.now(),
            completed=True
        )
        
        log1 = ExerciseLog.objects.create(
            workout_session=session,
            exercise_name='Bench Press',
            sets_completed=3,
            reps_per_set=[10, 8, 6]
        )
        
        log2 = ExerciseLog.objects.create(
            workout_session=session,
            exercise_name='Squat',
            sets_completed=4,
            reps_per_set=[12, 10, 8, 6]
        )
        
        self.assertEqual(session.exercise_logs.count(), 2)
        self.assertIn(log1, session.exercise_logs.all())
        self.assertIn(log2, session.exercise_logs.all())
    
    def test_user_cascade_deletion(self):
        """Test that related objects are deleted when user is deleted."""
        # Create related objects
        session = WorkoutSession.objects.create(
            user=self.user,
            start_time=timezone.now(),
            completed=True
        )
        
        snapshot = ProgressSnapshot.objects.create(
            user=self.user,
            date=timezone.now().date(),
            weight=75.0
        )
        
        streak = Streak.objects.create(
            user=self.user,
            streak_type='workout',
            current_count=5,
            last_activity_date=timezone.now().date(),
            start_date=timezone.now().date()
        )
        
        meal = MealLog.objects.create(
            user=self.user,
            meal_type='lunch',
            food_items=[{'name': 'Salad', 'quantity': '1 bowl', 'calories': 100}],
            total_calories=100,
            meal_time=timezone.now()
        )
        
        achievement = Achievement.objects.create(
            user=self.user,
            achievement_type='test',
            title='Test Achievement',
            description='Test',
            badge_icon='test',
            points_awarded=10
        )
        
        # Verify objects exist
        self.assertEqual(WorkoutSession.objects.filter(user=self.user).count(), 1)
        self.assertEqual(ProgressSnapshot.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Streak.objects.filter(user=self.user).count(), 1)
        self.assertEqual(MealLog.objects.filter(user=self.user).count(), 1)
        self.assertEqual(Achievement.objects.filter(user=self.user).count(), 1)
        
        # Delete user and verify cascade deletion
        self.user.delete()
        
        self.assertEqual(WorkoutSession.objects.filter(user=self.user).count(), 0)
        self.assertEqual(ProgressSnapshot.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Streak.objects.filter(user=self.user).count(), 0)
        self.assertEqual(MealLog.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Achievement.objects.filter(user=self.user).count(), 0)
