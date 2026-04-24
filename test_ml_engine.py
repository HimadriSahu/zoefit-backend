#!/usr/bin/env python
"""
Test script to verify ML engine functionality
"""

import os
import sys
import django
from datetime import date

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.zoefit.settings')
django.setup()

from nutrition.ml.ml_engine import ml_nutrition_engine
from ai_features.models import HealthMetrics
from django.contrib.auth.models import User

def test_ml_engine():
    """Test ML engine with sample data"""
    print("Testing ML Nutrition Engine...")
    
    try:
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser_ml',
            defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
        )
        
        # Create test health metrics
        metrics, created = HealthMetrics.objects.get_or_create(
            user=user,
            defaults={
                'height': 175,
                'weight': 70,
                'target_weight': 68,
                'fitness_goal': 'weight_loss',
                'activity_level': 'moderate',
                'dietary_preferences': ['vegetarian'],
                'allergies': ['nuts'],
                'medical_conditions': []
            }
        )
        
        print(f"User: {user.username}")
        print(f"Metrics: Height={metrics.height}cm, Weight={metrics.weight}kg, Goal={metrics.fitness_goal}")
        
        # Test ML meal plan generation
        print("\nGenerating ML meal plan...")
        meal_plan = ml_nutrition_engine.generate_ml_meal_plan(metrics, date.today())
        
        print(f"Approach: {meal_plan.get('approach', 'unknown')}")
        print(f"Confidence: {meal_plan.get('confidence_score', 0):.3f}")
        print(f"Total Calories: {meal_plan.get('total_calories', 0)}")
        print(f"Protein: {meal_plan.get('protein', 0)}g")
        print(f"Carbs: {meal_plan.get('carbs', 0)}g")
        print(f"Fat: {meal_plan.get('fat', 0)}g")
        print(f"Model Version: {meal_plan.get('model_version', 'unknown')}")
        print(f"Adaptation Applied: {meal_plan.get('adaptation_applied', False)}")
        
        # Print meal details
        meals = meal_plan.get('meals', [])
        print(f"\nGenerated {len(meals)} meals:")
        for i, meal in enumerate(meals):
            print(f"\nMeal {i+1}: {meal.get('name', 'Unknown')}")
            print(f"  Calories: {meal.get('estimated_calories', 0)}")
            print(f"  Foods: {len(meal.get('foods', []))} items")
            for food in meal.get('foods', [])[:3]:  # Show first 3 foods
                print(f"    - {food.get('name', 'Unknown')}: {food.get('quantity', '0g')}")
        
        print("\n✅ ML Engine test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing ML engine: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ml_engine()
    sys.exit(0 if success else 1)
