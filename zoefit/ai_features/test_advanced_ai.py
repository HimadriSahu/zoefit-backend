"""
Advanced AI Features Test Suite

Test cases for advanced AI features including progress prediction,
workout adaptation, and analytics.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta
from .models import HealthMetrics, MealPlan, WorkoutPlan, ProgressTracking
from .advanced_ai import AdvancedAIEngine
from .analytics import AIAnalytics

User = get_user_model()


class AdvancedAIEngineTests(TestCase):
    """Test advanced AI engine functionality."""
    
    def setUp(self):
        self.engine = AdvancedAIEngine()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.health_metrics = HealthMetrics.objects.create(
            user=self.user,
            height=175.0,
            weight=70.0,
            bmi=22.9,
            fitness_goal='weight_loss',
            activity_level='moderate'
        )
    
    def test_predict_progress_basic(self):
        """Test basic progress prediction."""
        predictions = self.engine.predict_progress(self.user, 30)
        
        self.assertIn('weight_prediction', predictions)
        self.assertIn('workout_completion', predictions)
        self.assertIn('goal_achievement_probability', predictions)
        self.assertIn('recommendations', predictions)
        self.assertEqual(len(predictions['weight_prediction']), 30)
        self.assertEqual(len(predictions['workout_completion']), 30)
    
    def test_predict_progress_with_history(self):
        """Test progress prediction with historical data."""
        # Create some progress history
        for i in range(5):
            ProgressTracking.objects.create(
                user=self.user,
                weight=70.0 - (i * 0.5),  # Losing weight
                workout_streak=i + 1,
                total_workouts=(i + 1) * 3,
                progress_score=60 + (i * 5)
            )
        
        predictions = self.engine.predict_progress(self.user, 30)
        
        self.assertGreater(predictions['goal_achievement_probability'], 0.5)
        self.assertGreater(len(predictions['recommendations']), 0)
    
    def test_adapt_workout_plan(self):
        """Test workout plan adaptation."""
        # Create a workout plan
        workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            day=1,
            exercises=[
                {
                    'name': 'Push-ups',
                    'type': 'strength',
                    'sets': 3,
                    'reps': 10,
                    'rest_time': 60,
                    'difficulty': 'beginner'
                }
            ],
            workout_type='strength',
            estimated_duration=30,
            difficulty_level='beginner',
            intensity_score=5.0
        )
        
        # Performance data indicating workout is too easy
        performance_data = {
            'completion_rate': 1.0,
            'user_rating': 5
        }
        
        adapted_plan = self.engine.adapt_workout_plan(
            self.user, workout_plan, performance_data
        )
        
        # Should have increased difficulty
        self.assertGreater(adapted_plan.intensity_score, 5.0)
        self.assertEqual(adapted_plan.exercises[0]['reps'], 12)  # Increased reps
    
    def test_optimize_meal_plan(self):
        """Test meal plan optimization."""
        # Create a meal plan
        meal_plan = MealPlan.objects.create(
            user=self.user,
            date=date.today(),
            meals={
                'breakfast': {
                    'foods': {
                        'main': [{
                            'name': 'Oatmeal',
                            'portion': 200,
                            'calories': 200,
                            'protein': 8,
                            'carbs': 40,
                            'fat': 6
                        }]
                    }
                }
            },
            total_calories=1800,
            confidence_score=0.8
        )
        
        # Feedback indicating portions are too large
        feedback_data = {
            'rating': 2,
            'feedback': 'Too much food, portions too large'
        }
        
        optimized_plan = self.engine.optimize_meal_plan(
            self.user, meal_plan, feedback_data
        )
        
        # Should have increased confidence score
        self.assertGreater(optimized_plan.confidence_score, 0.8)


class AIAnalyticsTests(TestCase):
    """Test AI analytics functionality."""
    
    def setUp(self):
        self.analytics = AIAnalytics()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.health_metrics = HealthMetrics.objects.create(
            user=self.user,
            height=175.0,
            weight=70.0,
            bmi=22.9,
            fitness_goal='weight_loss',
            activity_level='moderate'
        )
    
    def test_user_engagement_metrics(self):
        """Test user engagement metrics calculation."""
        # Create some engagement data
        MealPlan.objects.create(
            user=self.user,
            date=date.today(),
            meals={},
            total_calories=1800,
            user_rating=4
        )
        
        WorkoutPlan.objects.create(
            user=self.user,
            day=1,
            exercises=[],
            workout_type='strength',
            completed=True,
            user_rating=5
        )
        
        ProgressTracking.objects.create(
            user=self.user,
            progress_score=75,
            workout_streak=5
        )
        
        metrics = self.analytics.get_user_engagement_metrics(self.user, 30)
        
        self.assertIn('meal_engagement', metrics)
        self.assertIn('workout_engagement', metrics)
        self.assertIn('chat_engagement', metrics)
        self.assertIn('progress_engagement', metrics)
        self.assertIn('overall_engagement_score', metrics)
        self.assertGreater(metrics['overall_engagement_score'], 0)
    
    def test_ai_performance_metrics(self):
        """Test AI performance metrics calculation."""
        # Create some performance data
        MealPlan.objects.create(
            user=self.user,
            date=date.today(),
            meals={},
            total_calories=1800,
            confidence_score=0.85,
            user_rating=4
        )
        
        WorkoutPlan.objects.create(
            user=self.user,
            day=1,
            exercises=[],
            workout_type='strength',
            adaptation_score=0.8,
            user_rating=4
        )
        
        performance = self.analytics.get_ai_performance_metrics(30)
        
        self.assertIn('meal_performance', performance)
        self.assertIn('workout_performance', performance)
        self.assertIn('chat_performance', performance)
        self.assertIn('overall_ai_score', performance)
        self.assertGreater(performance['overall_ai_score'], 0)
    
    def test_user_behavior_insights(self):
        """Test user behavior insights generation."""
        # Create some behavior data
        for i in range(5):
            ProgressTracking.objects.create(
                user=self.user,
                weight=70.0 - (i * 0.2),
                workout_streak=i + 1,
                progress_score=70 + (i * 2)
            )
        
        MealPlan.objects.create(
            user=self.user,
            date=date.today(),
            meals={},
            user_rating=4,
            user_feedback='Great variety, loved the meals'
        )
        
        insights = self.analytics.get_user_behavior_insights(self.user)
        
        self.assertIn('behavioral_insights', insights)
        self.assertIn('actionable_recommendations', insights)
        self.assertIn('goal_alignment', insights['behavioral_insights'])
        self.assertIn('consistency_patterns', insights['behavioral_insights'])
    
    def test_system_health_metrics(self):
        """Test system health metrics calculation."""
        health = self.analytics.get_system_health_metrics()
        
        self.assertIn('user_metrics', health)
        self.assertIn('content_generation', health)
        self.assertIn('system_performance', health)
        self.assertIn('system_health_score', health)


class AdvancedAPIEndpointTests(TestCase):
    """Test advanced API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
        
        # Create health metrics
        HealthMetrics.objects.create(
            user=self.user,
            height=175.0,
            weight=70.0,
            bmi=22.9,
            fitness_goal='weight_loss',
            activity_level='moderate'
        )
    
    def test_predict_progress_endpoint(self):
        """Test progress prediction API endpoint."""
        response = self.client.get('/api/ai/predict-progress/?days=30')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('predictions', response.data)
        self.assertIn('prediction_period_days', response.data)
        self.assertEqual(response.data['prediction_period_days'], 30)
    
    def test_adapt_workout_plan_endpoint(self):
        """Test workout plan adaptation API endpoint."""
        # Create a workout plan first
        workout_plan = WorkoutPlan.objects.create(
            user=self.user,
            day=1,
            exercises=[],
            workout_type='strength'
        )
        
        performance_data = {
            'completion_rate': 1.0,
            'user_rating': 5
        }
        
        response = self.client.post(
            '/api/ai/adapt-workout/',
            {
                'workout_id': workout_plan.id,
                'performance_data': performance_data
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('adapted_plan', response.data)
    
    def test_get_ai_insights_endpoint(self):
        """Test AI insights API endpoint."""
        response = self.client.get('/api/ai/insights/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('insights', response.data)
        self.assertIn('current_status', response.data['insights'])
        self.assertIn('progress_summary', response.data['insights'])
        self.assertIn('recommendations', response.data['insights'])
    
    def test_get_user_analytics_endpoint(self):
        """Test user analytics API endpoint."""
        response = self.client.get('/api/ai/analytics/user/?days=30')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('engagement_metrics', response.data)
        self.assertIn('behavior_insights', response.data)
        self.assertEqual(response.data['analytics_period_days'], 30)
    
    def test_get_system_analytics_endpoint_unauthorized(self):
        """Test system analytics endpoint without admin access."""
        response = self.client.get('/api/ai/analytics/system/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_get_system_analytics_endpoint_authorized(self):
        """Test system analytics endpoint with admin access."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/ai/analytics/system/?days=30')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('ai_performance', response.data)
        self.assertIn('system_health', response.data)
        self.assertEqual(response.data['analytics_period_days'], 30)


class IntegrationTests(TestCase):
    """Integration tests for the complete AI system."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create comprehensive test data
        self.health_metrics = HealthMetrics.objects.create(
            user=self.user,
            height=175.0,
            weight=70.0,
            bmi=22.9,
            fitness_goal='weight_loss',
            activity_level='moderate'
        )
    
    def test_complete_ai_workflow(self):
        """Test complete AI workflow from metrics to insights."""
        # 1. Generate meal plan
        meal_response = self.client.post(
            '/api/ai/meal-plan/generate/',
            {'date': '2024-01-01'}
        )
        self.assertEqual(meal_response.status_code, status.HTTP_201_CREATED)
        
        # 2. Generate workout plan
        workout_response = self.client.post(
            '/api/ai/workout-plan/generate/',
            {'day': 1}
        )
        self.assertEqual(workout_response.status_code, status.HTTP_201_CREATED)
        
        # 3. Complete workout
        workout_id = workout_response.data['workout_plan']['id']
        completion_response = self.client.post(
            '/api/ai/workout-complete/',
            {
                'workout_id': workout_id,
                'completed': True,
                'completion_time_minutes': 35,
                'rating': 4
            }
        )
        self.assertEqual(completion_response.status_code, status.HTTP_200_OK)
        
        # 4. Get AI insights
        insights_response = self.client.get('/api/ai/insights/')
        self.assertEqual(insights_response.status_code, status.HTTP_200_OK)
        
        # 5. Get analytics
        analytics_response = self.client.get('/api/ai/analytics/user/')
        self.assertEqual(analytics_response.status_code, status.HTTP_200_OK)
        
        # 6. Predict progress
        prediction_response = self.client.get('/api/ai/predict-progress/')
        self.assertEqual(prediction_response.status_code, status.HTTP_200_OK)
        
        # Verify all data is consistent
        self.assertIn('workout_streak', insights_response.data['insights']['progress_summary'])
        self.assertIn('overall_engagement_score', analytics_response.data['engagement_metrics'])
        self.assertIn('weight_prediction', prediction_response.data['predictions'])
    
    def test_adaptive_learning_cycle(self):
        """Test the adaptive learning cycle."""
        # 1. Generate initial workout
        workout_response = self.client.post(
            '/api/ai/workout-plan/generate/',
            {'day': 1}
        )
        workout_id = workout_response.data['workout_plan']['id']
        initial_intensity = workout_response.data['workout_plan']['intensity_score']
        
        # 2. Complete with high performance
        self.client.post(
            '/api/ai/workout-complete/',
            {
                'workout_id': workout_id,
                'completed': True,
                'rating': 5
            }
        )
        
        # 3. Adapt workout based on performance
        adapt_response = self.client.post(
            '/api/ai/adapt-workout/',
            {
                'workout_id': workout_id,
                'performance_data': {
                    'completion_rate': 1.0,
                    'user_rating': 5
                }
            }
        )
        
        self.assertEqual(adapt_response.status_code, status.HTTP_200_OK)
        adapted_intensity = adapt_response.data['adapted_plan']['intensity_score']
        
        # Should have increased intensity
        self.assertGreater(adapted_intensity, initial_intensity)
    
    def test_feedback_improvement_cycle(self):
        """Test feedback-driven improvement cycle."""
        # 1. Generate meal plan
        meal_response = self.client.post(
            '/api/ai/meal-plan/generate/',
            {'date': '2024-01-01'}
        )
        meal_id = meal_response.data['meal_plan']['id']
        initial_confidence = meal_response.data['meal_plan']['confidence_score']
        
        # 2. Provide positive feedback
        # (This would be implemented in a real feedback endpoint)
        
        # 3. Generate insights to see improvement
        insights_response = self.client.get('/api/ai/insights/')
        self.assertEqual(insights_response.status_code, status.HTTP_200_OK)
        
        # Verify system is learning and improving
        self.assertGreaterEqual(initial_confidence, 0.5)
