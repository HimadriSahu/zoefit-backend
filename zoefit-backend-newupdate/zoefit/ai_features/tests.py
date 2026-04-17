"""
AI Features Tests

Test cases for AI-powered fitness features.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import HealthMetrics, AIChatHistory, ProgressTracking
from .ai_engine import AIRecommendationEngine
from .chatbot import EnhancedAIChatbot

User = get_user_model()


class AIRecommendationEngineTests(TestCase):
    """Test AI recommendation engine functionality."""
    
    def setUp(self):
        self.engine = AIRecommendationEngine()
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
            fitness_goal='maintenance',
            activity_level='moderate'
        )
    
    def test_generate_meal_plan(self):
        """Test meal plan generation."""
        from datetime import date
        meal_plan = self.engine.generate_meal_plan(self.health_metrics, date.today())
        
        self.assertIn('meals', meal_plan)
        self.assertIn('total_calories', meal_plan)
        self.assertIn('confidence_score', meal_plan)
        self.assertGreater(meal_plan['total_calories'], 0)
        self.assertGreaterEqual(meal_plan['confidence_score'], 0)
        self.assertLessEqual(meal_plan['confidence_score'], 1)
    
    def test_generate_workout_plan(self):
        """Test workout plan generation."""
        workout_plan = self.engine.generate_workout_plan(self.health_metrics, 1)
        
        self.assertIn('exercises', workout_plan)
        self.assertIn('workout_type', workout_plan)
        self.assertIn('estimated_duration', workout_plan)
        self.assertIn('difficulty_level', workout_plan)
        self.assertGreater(len(workout_plan['exercises']), 0)
        self.assertGreater(workout_plan['estimated_duration'], 0)


class AIChatbotTests(TestCase):
    """Test AI chatbot functionality."""
    
    def setUp(self):
        self.chatbot = EnhancedAIChatbot()
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
    
    def test_exercise_advice_intent(self):
        """Test exercise advice intent detection."""
        response = self.chatbot.process_message(
            "What exercises should I do for weight loss?", 
            self.health_metrics
        )
        
        self.assertIn('response', response)
        self.assertIn('intent', response)
        self.assertIn('confidence', response)
        self.assertEqual(response['intent'], 'exercise_advice')
        self.assertGreater(response['confidence'], 0)
    
    def test_nutrition_question_intent(self):
        """Test nutrition question intent detection."""
        response = self.chatbot.process_message(
            "How much protein should I eat?", 
            self.health_metrics
        )
        
        self.assertIn('response', response)
        self.assertIn('intent', response)
        self.assertEqual(response['intent'], 'nutrition_question')
        self.assertGreater(response['confidence'], 0)
    
    def test_motivation_intent(self):
        """Test motivation intent detection."""
        response = self.chatbot.process_message(
            "I'm feeling tired and unmotivated", 
            self.health_metrics
        )
        
        self.assertIn('response', response)
        self.assertIn('intent', response)
        self.assertEqual(response['intent'], 'motivation')
        self.assertGreater(response['confidence'], 0)


class HealthMetricsAPITests(TestCase):
    """Test Health Metrics API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_health_metrics(self):
        """Test creating health metrics."""
        data = {
            'height': 180.0,
            'weight': 75.0,
            'fitness_goal': 'muscle_gain',
            'activity_level': 'active',
            'dietary_preferences': {'diet_type': 'omnivore'},
            'medical_conditions': [],
            'allergies': ['nuts'],
            'target_weight': 80.0
        }
        
        response = self.client.post('/api/ai/health-metrics/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('metrics', response.data)
        
        # Check if health metrics were created
        metrics = HealthMetrics.objects.get(user=self.user)
        self.assertEqual(metrics.height, 180.0)
        self.assertEqual(metrics.weight, 75.0)
        self.assertEqual(metrics.fitness_goal, 'muscle_gain')
    
    def test_get_health_metrics(self):
        """Test retrieving health metrics."""
        # Create health metrics first
        HealthMetrics.objects.create(
            user=self.user,
            height=175.0,
            weight=70.0,
            bmi=22.9,
            fitness_goal='maintenance',
            activity_level='moderate'
        )
        
        response = self.client.get('/api/ai/health-metrics/get/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('height', response.data)
        self.assertIn('weight', response.data)
        self.assertIn('bmi', response.data)
        self.assertIn('fitness_goal', response.data)
        self.assertIn('activity_level', response.data)


class MealPlanAPITests(TestCase):
    """Test Meal Plan API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
    
    def test_generate_meal_plan(self):
        """Test meal plan generation."""
        data = {
            'date': '2024-01-01'
        }
        
        response = self.client.post('/api/ai/meal-plan/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('meal_plan', response.data)
        
        # Check if meal plan was created
        meal_plan = MealPlan.objects.get(user=self.user)
        self.assertIsNotNone(meal_plan.meals)
        self.assertGreater(meal_plan.total_calories, 0)


class WorkoutPlanAPITests(TestCase):
    """Test Workout Plan API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create health metrics
        HealthMetrics.objects.create(
            user=self.user,
            height=175.0,
            weight=70.0,
            bmi=22.9,
            fitness_goal='muscle_gain',
            activity_level='active'
        )
    
    def test_generate_workout_plan(self):
        """Test workout plan generation."""
        data = {
            'day': 1
        }
        
        response = self.client.post('/api/ai/workout-plan/generate/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('workout_plan', response.data)
        
        # Check if workout plan was created
        workout_plan = WorkoutPlan.objects.get(user=self.user)
        self.assertIsNotNone(workout_plan.exercises)
        self.assertGreater(workout_plan.estimated_duration, 0)


class AIChatAPITests(TestCase):
    """Test AI Chat API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_ai_chat(self):
        """Test AI chat endpoint."""
        data = {
            'message': 'What exercises should I do to build muscle?'
        }
        
        response = self.client.post('/api/ai/chat/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.data)
        self.assertIn('intent', response.data)
        self.assertIn('confidence', response.data)
        
        # Check if chat history was created
        self.assertTrue(
            self.user.ai_chats.filter(
                user_message='What exercises should I do to build muscle?'
            ).exists()
        )
