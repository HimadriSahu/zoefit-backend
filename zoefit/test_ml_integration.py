#!/usr/bin/env python
"""
Test script to verify ML integration
"""
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zoefit.settings')
django.setup()

def test_ml_integration():
    print("=== ZoeFit ML Integration Test ===")
    
    # Test 1: Check ML engine import
    try:
        from nutrition.ml.ml_engine import ml_nutrition_engine
        print("1. ML Engine Import: SUCCESS")
    except Exception as e:
        print(f"1. ML Engine Import: FAILED - {e}")
        return False
    
    # Test 2: Check model loading
    try:
        if ml_nutrition_engine.models:
            print(f"2. Model Loading: SUCCESS - {len(ml_nutrition_engine.models)} models loaded")
            print(f"   Models: {list(ml_nutrition_engine.models.keys())}")
        else:
            print("2. Model Loading: FAILED - No models loaded")
            return False
    except Exception as e:
        print(f"2. Model Loading: FAILED - {e}")
        return False
    
    # Test 3: Check AI engine integration
    try:
        from ai_features.ai_engine import AIRecommendationEngine, ML_AVAILABLE
        print(f"3. AI Engine Integration: SUCCESS - ML_AVAILABLE = {ML_AVAILABLE}")
    except Exception as e:
        print(f"3. AI Engine Integration: FAILED - {e}")
        return False
    
    # Test 4: Test meal plan generation
    try:
        from ai_features.models import HealthMetrics
        from authentication.models import User
        from datetime import date
        
        # Create a test user if not exists
        user, created = User.objects.get_or_create(
            username='test_ml_user',
            defaults={'email': 'test@example.com'}
        )
        
        # Create user profile first
        from users.models import UserProfile
        from datetime import date
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'date_of_birth': date(1994, 1, 1),  # 30 years old
                'gender': 'male',
                'height': 175,
                'weight': 70,
                'fitness_goal': 'maintain',
                'activity_level': 'moderate',
                'target_weight': 70
            }
        )
        
        # Create test health metrics
        metrics, created = HealthMetrics.objects.get_or_create(
            user=user,
            defaults={
                'height': 175,
                'weight': 70,
                'bmi': 22.9,
                'fitness_goal': 'maintenance',
                'activity_level': 'moderate',
                'target_weight': 70
            }
        )
        
        # Generate meal plan
        engine = AIRecommendationEngine()
        meal_plan = engine.generate_meal_plan(metrics, date.today())
        
        print(f"4. Meal Plan Generation: SUCCESS")
        print(f"   Approach: {meal_plan.get('approach', 'unknown')}")
        print(f"   Confidence: {meal_plan.get('model_confidence', 'N/A')}")
        print(f"   Meals: {len(meal_plan.get('meals', []))}")
        
    except Exception as e:
        print(f"4. Meal Plan Generation: FAILED - {e}")
        return False
    
    print("\n=== All Tests Passed! ===")
    return True

if __name__ == '__main__':
    test_ml_integration()
